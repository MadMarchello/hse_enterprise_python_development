Флаг -e (editable) ставит оба пакета «в разработку»: 
правите код в src/ — изменения сразу видны без переустановки.

```bash
cd hse_enterprise_python_development
python3 -m venv .venv
source .venv/bin/activate

pip install -e ./report_maile -e ./homework-02
```