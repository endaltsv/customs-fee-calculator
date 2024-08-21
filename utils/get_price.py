import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os

from bot.config import URL_CALCULATOR


def create_payload(data):
    payload = {
        "forCountry": "643",
        "age": data.get("age"),
        "price": data.get("price"),
        "currency": "392",
        "dtype": data.get("dtype"),
        "obyem": data.get("obyem"),
        "pwr_val": data.get("pwr_val"),
        "pwr": data.get("pwr"),
        "hybrid1": data.get("hybrid1"),
        "lico": data.get("lico")
    }

    if data.get("hybrid1") != "1" and data.get("hybrid2"):
        payload["hybrid2"] = data.get("hybrid2")

    return payload


def wrap_text(text, width=17):
    return "\n".join([text[i:i + width] for i in range(0, len(text), width)])


def clean_text(text, apply_wrapping=False):
    text = text.replace(
        "Расчет утилиза­ционного сбора (новые, ввозимые ФИЗИЧЕСКИМИ ЛИЦАМИ ДЛЯ ПРОДАЖИ с рабочим объемом двигателя свыше 1000 см3,)",
        "Расчет утилизационного сбора")
    text = text.replace(
        "Расчет утилиза­ционного сбора (новые, ввозимые ФИЗИЧЕСКИМИ ЛИЦАМИ ДЛЯ ЛИЧНОГО ПОЛЬЗОВАНИЯ с рабочим объемом двигателя свыше 1000 см3,)",
        "Расчет утилизационного сбора")
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\d+)\s+(руб|JPY|евро)', r'\1 \2', text)
    return wrap_text(text) if apply_wrapping else text


def get_table_data(table, apply_wrapping=False):
    rows = table.find_all('tr')
    table_data = []

    for row in rows:
        cols = row.find_all(['th', 'td'])
        cols_text = [clean_text(col.get_text(separator=" ", strip=True), apply_wrapping) for col in cols]
        table_data.append(cols_text)

    return table_data


def create_table_image(table_data, title, filename, add_total_separator=False, apply_wrapping=False):
    total_row = table_data.pop(-1) if add_total_separator else None

    df = pd.DataFrame(table_data[1:], columns=table_data[0])

    if total_row and len(total_row) < len(df.columns):
        total_row.extend([''] * (len(df.columns) - len(total_row)))

    if add_total_separator:
        df.loc[len(df)] = ['-' * 20] * len(df.columns)
        df.loc[len(df)] = total_row

    fig, ax = plt.subplots(figsize=(12, len(df) * 1.2))
    ax.axis('tight')
    ax.axis('off')

    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2.5)

    for key, cell in table.get_celld().items():
        if apply_wrapping:
            cell.set_text_props(wrap=True)
            cell.set_height(cell.get_height() * 1.5)

    plt.title(title, fontsize=18, pad=-10)

    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()


def merge_images(image1_path, image2_path, output_path):
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    total_width = max(image1.width, image2.width)
    total_height = image1.height + image2.height

    merged_image = Image.new('RGB', (total_width, total_height - 50), (255, 255, 255))

    merged_image.paste(image1, (0, 0))
    merged_image.paste(image2, (0, image1.height - 50))
    crop_height_top = 600
    merged_image = merged_image.crop((0, crop_height_top, total_width, total_height - 50))
    merged_image.save(output_path)

    os.remove(image1_path)
    os.remove(image2_path)

    return output_path


def get_price_and_create_image(payload):
    url = URL_CALCULATOR

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table', class_='bordered col-100 pAutoVat_result_table table-mobile')

        if tables:
            table_data_1 = get_table_data(tables[0], apply_wrapping=False)
            create_table_image(table_data_1, "Схема расчета", "table_1.png", add_total_separator=False,
                               apply_wrapping=False)

            if len(tables) > 1:
                table_data_2 = get_table_data(tables[1], apply_wrapping=True)
                create_table_image(table_data_2, "Расчет платежа", "table_2.png",
                                   add_total_separator=True, apply_wrapping=True)

                merged_image_path = merge_images("table_1.png", "table_2.png", "merged_table.png")

                return merged_image_path

        return "Таблицы не найдены."
    else:
        return f"Ошибка при запросе: {response.status_code}"
