"""Aggregate per-model metrics CSV files into a single ML_Overall_Result.csv.

읽기 대상:
  ../CatBoost/*metrics*seen*.csv
  ../Random_Forest/*metrics*seen*.csv
  ../XGBoost/*metrics*seen*.csv

출력 포맷 (열 순서 고정):
	model,target,R2,MAE,RMSE  (요청에 따라 R2와 RMSE 위치 교환)

사용법:
  python aggregate_result.py               # 기본 실행, 파일 생성/갱신
  python aggregate_result.py --round 6      # 소수 자릿수 지정 (기본 6)

추가 특징:
  - 패턴에 맞는 metrics CSV 1개만 선택. 여러개면 최신(mtime) 사용.
  - 누락되거나 열 이름이 다른 경우 예외 메시지 출력 후 건너뜀.
  - 기존 결과와 내용이 동일하면 덮어쓰기만 하고 메시지 표시.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List
import sys

try:
	import pandas as pd  # type: ignore
except ImportError:  # pragma: no cover - pandas 필수
	print("[ERROR] pandas 미설치. 설치: pip install pandas", file=sys.stderr)
	raise


@dataclass
class ModelSpec:
	name: str          # 출력될 model 이름
	folder: str        # 상위 디렉토리 내 폴더명
	pattern: str = "metrics_seen"  # 파일명 패턴 일부

	def find_metrics_file(self, base_dir: Path) -> Path | None:
		model_dir = base_dir / self.folder
		if not model_dir.is_dir():
			return None
		candidates = [
			p for p in model_dir.glob("*" )
			if p.is_file() and self.pattern in p.name and p.suffix.lower() == ".csv"
		]
		if not candidates:
			return None
		# 최신 수정시간 선택
		candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
		return candidates[0]


REQUIRED_COLUMNS = ["target", "R2", "MAE", "RMSE"]
OUTPUT_COLUMNS = ["model", "target", "R2", "MAE", "RMSE"]


def load_metrics(path: Path) -> pd.DataFrame:
	df = pd.read_csv(path)
	missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
	if missing:
		raise ValueError(f"{path.name} 열 누락: {missing}")
	return df[REQUIRED_COLUMNS].copy()


def aggregate(specs: List[ModelSpec], round_digits: int) -> pd.DataFrame:
	base_dir = Path(__file__).resolve().parents[1]
	rows = []
	for spec in specs:
		metrics_path = spec.find_metrics_file(base_dir)
		if not metrics_path:
			print(f"[WARN] {spec.name}: metrics CSV를 찾지 못했습니다.")
			continue
		try:
			df = load_metrics(metrics_path)
		except Exception as e:  # noqa: BLE001
			print(f"[ERROR] {spec.name} 불러오기 실패: {e}")
			continue
		df.insert(0, "model", spec.name)
		rows.append(df)
		print(f"[INFO] {spec.name}: '{metrics_path.name}' 로드 (행 {len(df)})")

	if not rows:
		raise SystemExit("집계할 데이터가 없습니다.")

	out = pd.concat(rows, ignore_index=True)
	# 숫자 반올림
	for col in ["R2", "MAE", "RMSE"]:
		out[col] = out[col].astype(float).round(round_digits)
	# 열 순서 정렬
	out = out[OUTPUT_COLUMNS]
	# model 순서 및 target 사전순(또는 원본 순서) 유지: specs 순서 기준
	category_order = {name: i for i, name in enumerate([s.name for s in specs])}
	target_order_list = ["CETR", "GETR", "TSTA", "TSDA"]
	target_order = {t: i for i, t in enumerate(target_order_list)}

	def _sort_key(series):
		if series.name == "model":
			return series.map(category_order)
		if series.name == "target":
			return series.map(target_order)
		return series

	out.sort_values(by=["model", "target"], key=_sort_key, inplace=True)
	out.reset_index(drop=True, inplace=True)
	return out


def write_csv(df: pd.DataFrame, path: Path):
	# pandas to_csv 는 공백 trimming 힘드니 csv.writer 로 제어
	with path.open("w", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(OUTPUT_COLUMNS)
		for _, row in df.iterrows():
			writer.writerow([row[c] for c in OUTPUT_COLUMNS])


def main(argv: List[str] | None = None) -> int:
	parser = argparse.ArgumentParser(description="집계 ML metrics CSV 생성")
	parser.add_argument("--round", type=int, default=6, help="소수 반올림 자릿수 (기본 6)")
	parser.add_argument(
		"--output", type=Path, default=Path(__file__).with_name("ML_Overall_Result.csv"), help="출력 CSV 경로"
	)
	args = parser.parse_args(argv)

	specs = [
		ModelSpec(name="XGBoost", folder="ML_XGBoost", pattern="metrics_seen"),
		ModelSpec(name="CatBoost", folder="ML_CatBoost", pattern="metrics_seen"),
		ModelSpec(name="RandomForest", folder="ML_Random_Forest", pattern="metrics_seen"),
	]

	df = aggregate(specs, args.round)
	write_csv(df, args.output)
	print(f"[DONE] 결과 저장: {args.output} (행 {len(df)})")
	return 0


if __name__ == "__main__":  # pragma: no cover
	raise SystemExit(main())

