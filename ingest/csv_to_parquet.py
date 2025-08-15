import argparse
import pathlib as P
import polars as pl


def main(src: str, dst: str) -> None:
    src_p = P.Path(src)
    dst_p = P.Path(dst)
    dst_p.mkdir(parents=True, exist_ok=True)
    count = 0
    for csv in src_p.glob("*.csv"):
        try:
            df = pl.read_csv(csv, infer_schema_length=10000)
            out = dst_p / csv.with_suffix(".parquet").name
            df.write_parquet(out)
            print(f"ok: {out.name}")
            count += 1
        except Exception as e:
            print(f"skip: {csv.name} - {e}")
    print("Converted", count, "files")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="Input raw CSV directory")
    ap.add_argument("dst", help="Output Parquet directory")
    args = ap.parse_args()
    main(args.src, args.dst)
