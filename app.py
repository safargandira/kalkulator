import ast
import operator
import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OPERATOR = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def hitung(node):
    if isinstance(node, ast.Expression):
        return hitung(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATOR:
        return OPERATOR[type(node.op)](hitung(node.left), hitung(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATOR:
        return OPERATOR[type(node.op)](hitung(node.operand))
    raise ValueError("Ekspresi tidak valid")


def format_angka(nilai):
    if isinstance(nilai, float) and nilai.is_integer():
        nilai = int(nilai)
    if isinstance(nilai, float):
        nilai = round(nilai, 10)
    return str(nilai)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/hitung", methods=["POST"])
def api_hitung():
    data = request.get_json(silent=True) or {}
    ekspresi = str(data.get("ekspresi", "")).replace("×", "*").replace("÷", "/")
    if not ekspresi or len(ekspresi) > 100:
        return jsonify(error="Ekspresi kosong atau terlalu panjang"), 400
    try:
        hasil = hitung(ast.parse(ekspresi, mode="eval"))
    except ZeroDivisionError:
        return jsonify(error="Tidak bisa dibagi nol"), 400
    except (ValueError, SyntaxError, OverflowError):
        return jsonify(error="Ekspresi tidak valid"), 400
    return jsonify(hasil=format_angka(hasil))


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))