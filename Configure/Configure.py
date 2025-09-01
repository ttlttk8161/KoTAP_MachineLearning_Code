"""집계된 ML_Overall_Result.csv 로부터 모델별 성능을 한 그림에 시각화.

사용법:
    python Configure.py \
        --input ML_Overall_Result.csv \
        --output ml_metrics_comparison.png \
        --dpi 160

기능:
  - 3개의 가로 서브플롯: RMSE, MAE, R2
  - Target 순서: CETR, GETR, TSTA, TSDA
  - Model 순서: XGBoost, CatBoost, RandomForest
  - 막대 위 값 표기 (소수 4자리)
  - --scale 옵션으로 (예: 1000) 값을 곱해 보기 쉽게 조정 가능 (표기 단위 함께 표시)
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

TARGET_ORDER = ["CETR", "GETR", "TSTA", "TSDA"]
MODEL_ORDER = ["XGBoost", "CatBoost", "RandomForest"]
METRICS = ["RMSE", "MAE", "R2"]  # 출력 순서


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # 기대되는 열 확인
    required = {"model", "target", "R2", "MAE", "RMSE"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"누락된 열: {missing}")
    # 카테고리 정렬
    df = df.copy()
    df['target'] = pd.Categorical(df['target'], categories=TARGET_ORDER, ordered=True)
    df['model'] = pd.Categorical(df['model'], categories=MODEL_ORDER, ordered=True)
    df.sort_values(["target", "model"], inplace=True)
    return df


def plot(df: pd.DataFrame, output: Path, dpi: int, scale: float, annotate_decimals: int):
    plt.rcParams.update({"font.size": 11})
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)

    bar_width = 0.22
    x_idx = range(len(TARGET_ORDER))

    colors = {
        "XGBoost": "#1f77b4",  # 파랑
        "CatBoost": "#ff7f0e",  # 주황
        "RandomForest": "#2ca02c",  # 초록
    }

    for ax, metric in zip(axes, METRICS):
        ax.set_title(f"{metric} Comparison")
        for i, model in enumerate(MODEL_ORDER):
            sub = df[df['model'] == model]
            vals = sub[metric].astype(float).values * scale
            # 막대 x 위치 오프셋
            offs = [x + (i - (len(MODEL_ORDER)-1)/2)*bar_width for x in x_idx]
            bars = ax.bar(offs, vals, width=bar_width, label=model, color=colors.get(model))
            # 주석
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width()/2, b.get_height() + (max(vals)*0.01 if max(vals) else 0.001),
                        f"{v:.{annotate_decimals}f}", ha='center', va='bottom', fontsize=9, rotation=0)
        ax.set_xticks(list(x_idx))
        ax.set_xticklabels(TARGET_ORDER)
        ax.set_xlabel("Target Variables")
        ax.set_ylabel(metric + (f" (x{int(scale)})" if scale != 1 else ""))
        ax.grid(axis='y', linestyle='--', alpha=0.4)

    axes[0].legend(loc='upper right')
    fig.suptitle("Model Performance Comparison", fontsize=16)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi)
    print(f"[DONE] 저장: {output}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, default=Path('ML_Overall_Result.csv'))
    p.add_argument('--output', type=Path, default=Path('ml_metrics_comparison.png'))
    p.add_argument('--dpi', type=int, default=150)
    p.add_argument('--scale', type=float, default=1.0, help='표시용 스케일링 (예: 100 또는 1000)')
    p.add_argument('--decimals', type=int, default=4, help='막대 위 주석 소수 자릿수')
    args = p.parse_args()

    df = load_data(args.input)
    plot(df, args.output, dpi=args.dpi, scale=args.scale, annotate_decimals=args.decimals)


if __name__ == '__main__':
    main()
