import argparse, pathlib as P, duckdb

def main(db: str, pq_dir: str):
    con = duckdb.connect(db)
    pq = P.Path(pq_dir)
    for p in pq.glob("*.parquet"):
        t = p.stem  # dosya adı -> tablo adı
        con.execute(f"DROP TABLE IF EXISTS {t}")
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_parquet('{p.as_posix()}')")
        print("Loaded", t)
    con.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("pq_dir")
    args = ap.parse_args()
    main(args.db, args.pq_dir)
