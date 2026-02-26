import os
import re
import argparse
import qrcode

def safe_filename(s: str) -> str:
    """
    把内容转换成安全的文件名（避免 / \ : * ? " < > | 等非法字符）
    """
    s = s.strip()
    s = re.sub(r'[\\/:*?"<>|]+', "_", s)
    return s if s else "empty"

def read_values(input_path: str) -> list[str]:
    """
    读取“单列数据”：
    - .txt: 每行一个值
    - .csv: 默认取第一列（可包含表头；空行跳过）
    """
    values = []
    ext = os.path.splitext(input_path)[1].lower()

    if ext == ".txt":
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                v = line.strip()
                if v:
                    values.append(v)

    elif ext == ".csv":
        import csv
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                v = str(row[0]).strip()
                # 跳过空值
                if v:
                    values.append(v)
    else:
        raise ValueError("只支持 .txt 或 .csv 输入文件")

    return values

def make_qr(text: str, out_path: str, box_size: int = 10, border: int = 4):
    """
    生成单个二维码 PNG
    """
    qr = qrcode.QRCode(
        version=None,  # 自动选择版本
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)

def main():
    parser = argparse.ArgumentParser(description="批量把一列数字/文本生成二维码 PNG")
    parser.add_argument("-i", "--input", required=True, help="输入文件：.txt(每行一个) 或 .csv(取第一列)")
    parser.add_argument("-o", "--output", default="qr_output", help="输出文件夹（默认 qr_output）")
    parser.add_argument("--prefix", default="", help="输出文件名前缀（可选）")
    parser.add_argument("--box-size", type=int, default=10, help="二维码像素块大小（默认10）")
    parser.add_argument("--border", type=int, default=4, help="二维码边框大小（默认4）")
    args = parser.parse_args()

    values = read_values(args.input)
    if not values:
        print("输入文件没有有效数据。")
        return

    os.makedirs(args.output, exist_ok=True)

    used_names = set()
    count = 0
    for v in values:
        base = safe_filename(v)
        name = f"{args.prefix}{base}.png" if args.prefix else f"{base}.png"

        # 防止重复值导致覆盖：自动加 _2 _3 ...
        final_name = name
        idx = 2
        while final_name in used_names or os.path.exists(os.path.join(args.output, final_name)):
            stem, ext = os.path.splitext(name)
            final_name = f"{stem}_{idx}{ext}"
            idx += 1

        out_path = os.path.join(args.output, final_name)
        make_qr(v, out_path, box_size=args.box_size, border=args.border)
        used_names.add(final_name)
        count += 1

    print(f"完成：共生成 {count} 个二维码，输出到：{os.path.abspath(args.output)}")

if __name__ == "__main__":
    main()