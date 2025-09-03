lag_ 파생 컬럼이 없는 원본 컬럼 전체 목록은 아래와 같습니다.

- name
- stock
- year
- KOSPI
- fnd_year
- fiscal
- ind
- big4
- forn
- own
- inv
- cogs
- dep
- tax
- rec
- ocf
- cash
- tan
- land
- cip
- intan
- c_liab (lag_c_liab는 있지만, c_liab 자체도 원본 컬럼)
- c_asset (lag_c_asset는 있지만, c_asset 자체도 원본 컬럼)
- SIZE
- LEV
- CUR
- GRW
- ROA
- ROE
- CFO
- PPE
- AGE
- INVREC
- MB
- TQ
- LOSS
- GETR
- CETR
- GETR3
- CETR3
- GETR5
- CETR5
- TSTA
- TSDA
- A_GETR
- A_CETR
- A_GETR3
- A_CETR3
- A_GETR5
- A_CETR5

즉, lag_ 파생 컬럼이 없는 컬럼이 위 목록입니다.  
추가로 궁금한 점이 있으면 말씀해 주세요!

아래는 원본 컬럼명에서 lag_가 붙은 컬럼과, 그에 해당하는 원본 컬럼의 매칭 리스트입니다.

| lag_ 컬럼명      | 원본 컬럼명  |
|------------------|-------------|
| lag_asset        | asset       |
| lag_liab         | liab        |
| lag_equit        | equit       |
| lag_sales        | sales       |
| lag_total        | total       |
| lag1_ni          | ni          |
| lag_c_asset      | c_asset     |
| lag_c_liab       | c_liab      |

즉, 아래 컬럼들에 대해 lag_ 파생 컬럼이 존재합니다:
- asset
- liab
- equit
- sales
- total
- ni (lag1_ni)
- c_asset
- c_liab

필요하다면, lag_가 없는 원본 컬럼 전체 목록도 제공해드릴 수 있습니다.



사소하지만, lag column으로인해 2010년도 데이터값도 몇몇 파악이 됨.