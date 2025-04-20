# RiichiCity-to-Tenhou-Log-Parser

## Summary
The code parses game logs from Riichi City(麻雀一番街) and exports them into Tenhou-format game records. 

The exported records are split by individual kyoku (局, single rounds) rather than combined into a full hanchan (半荘).

## Usage
Download the paifu (牌譜, game record) logs from [zx-api.pesiu.org](https://zx-api.pesiu.org) using the paifu ID, then run the command:
```
python convert.py <riichi_city_log_file> <tenhou6_log_file>
```
