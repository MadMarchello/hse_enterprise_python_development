# Homework 01

Проект по дисциплине «Промышленное программирование на Python».

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements.txt
python -m homework.main
```

### Отключение venv 
```bash
deactivate
```



## Зачем `__init__.py`

Файл `src/homework/__init__.py` в этом проекте пустой: логики в нём нет.

Исторически Python считал пакетом только каталог, в котором есть `__init__.py`. Без него `import homework` не работал. С Python 3.3 (PEP 420) каталог может быть namespace package и без этого файла; у нас пакет и так находится через `src` и `pip install -e .`.

Пустой `__init__.py` оставлен как явный маркер пакета и требование структуры задания, а не как часть программы.

## Стабильный вывод `set`

Порядок элементов множества в Python не фиксирован. Без отдельной обработки `str({...})` берёт текущий порядок обхода, и одна и та же программа может дать разный текст отчёта — а значит, разные MD5 и SHA-256.

Поэтому в `_format_value` множество распознаётся через `isinstance(value, set)`, элементы сортируются и только потом собираются в строку.

Для целых чисел разницы часто не видно: хеш `int` не рандомизируется, и `{3, 1, 2}` почти всегда печатается одинаково.

```text
# и со sorted, и с обычным str({3, 1, 2})
{1, 2, 3}
```

Разница проявляется на строках. Без `isinstance` вывод зависит от `PYTHONHASHSEED`:

```text
# PYTHONHASHSEED=0, только str(set)
{'python', 'course', 'homework'}

# PYTHONHASHSEED=42, только str(set)
{'homework', 'course', 'python'}
```

С `isinstance` и сортировкой по `repr` строка всегда одна и та же:

```text
{'course', 'homework', 'python'}
```
