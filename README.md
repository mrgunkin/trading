# Bitcoin Liquidation Map

## Описание
Этот скрипт собирает данные с Binance API по паре BTC/USDT за последние сутки (1h свечи), находит точку с максимальным объемом и рассчитывает уровни ликвидации для различных плеч (10x, 25x, 50x). Затем строится график ликвидационных уровней с указанием входной цены (Entry Price) и текущей цены (Current Price) в реальном времени.

## Как работает скрипт
1. **Получение данных**: Загружаются 1-часовые свечи BTC/USDT за последние сутки.
2. **Определение точки отсчета**: Находится свеча с максимальным объемом и фиксируется цена закрытия этой свечи как точка отсчета (Entry Price).
3. **Расчет ликвидационных уровней**: Для плеч 10x, 25x и 50x вычисляются уровни ликвидации в лонг и шорт.
4. **Построение графика**:
   - Отмечаются ликвидационные уровни цветными столбцами.
   - Наносятся линии Entry Price (зеленая) и текущей цены (серая) с их значениями.
5. **Вывод графика**: Отображается график ликвидационных уровней.

## Зависимости
- `requests`
- `pandas`
- `numpy`
- `matplotlib`

## Установка и запуск
```sh
pip install requests pandas numpy matplotlib
python script.py
```

## Пример вывода графика
График отображает ликвидационные уровни в зависимости от цены BTC, а также текущую и входную цену.

![Liquidation Map](Figure_1.png)

## Автор
**mrgunkin**  
[GitHub Profile](https://github.com/mrgunkin)

## Лицензия
MIT License
