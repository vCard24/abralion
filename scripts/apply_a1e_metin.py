# -*- coding: utf-8 -*-
"""A1e onayı: katalog metnini ve tablo etiketlerini TR/RU kayda geçirir. Ölçü satırına dokunmaz."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_RE = re.compile(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", re.S)
JSONLD_RE = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)',
    re.S,
)

TR_SLUGS = [
    "cam-seramik-matkap-ucu",
    "hss-matkap-ucu",
    "sds-plus-2-kesicili-beton-matkap-ucu",
    "sds-plus-4-kesicili-beton-matkap-ucu",
    "sds-max-burc-aleti",
    "miknatisli-anahtar-ucu",
    "ph2-manyetik-bits-uc",
    "duz-keski-sds-max",
    "sivri-uclu-keski-murc-sds-plus",
]
SIBLING = {
    "duz-keski-sds-max": "duz-keski-sds-plus",
    "sivri-uclu-keski-murc-sds-plus": "sivri-uclu-keski-murc-sds-max",
}


def esc(value: str) -> str:
    return (value or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def load_js(path: Path) -> tuple[str, dict]:
    raw = path.read_text(encoding="utf-8")
    match = CATALOG_RE.search(raw)
    if not match:
        raise SystemExit(f"katalog yok: {path}")
    return raw[: match.start(1)], json.loads(match.group(1))


def write_js(path: Path, prefix: str, catalog: dict) -> None:
    path.write_text(prefix + json.dumps(catalog, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def write_json(path: Path, catalog: dict) -> None:
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_labels(slug: str, variants: list[dict], lang: str) -> None:
    tr = lang == "tr"
    plus = "SDS-plus"
    max_ = "SDS-max"
    for variant in variants:
        if slug == "cam-seramik-matkap-ucu":
            variant["urun_tipi"] = (
                "Cam-seramik matkap ucu, 4 kesicili" if tr else "Сверло по стеклу и керамике, 4 резца"
            )
            variant["saft_tipi"] = (
                '1/4" Altıgen (Hex) / Silindirik' if tr else '1/4" шестигранный (Hex) / цилиндрический'
            )
        elif slug == "hss-matkap-ucu":
            variant["urun_tipi"] = "HSS matkap ucu" if tr else "Сверло HSS"
        elif slug == "sds-plus-2-kesicili-beton-matkap-ucu":
            variant["urun_tipi"] = (
                "Beton matkap ucu, 2 kesicili" if tr else "Бур по бетону, 2 резца"
            )
            variant["baglanti_tipi"] = plus
        elif slug == "sds-plus-4-kesicili-beton-matkap-ucu":
            variant["urun_tipi"] = (
                "Beton matkap ucu, 4 kesicili (Quadro)" if tr else "Бур по бетону, 4 резца (Quadro)"
            )
            variant["baglanti_tipi"] = plus
        elif slug == "sds-max-burc-aleti":
            variant["baglanti_tipi"] = max_
            variant["kafa_olcusu_mm"] = "45×45 mm"
        elif slug == "miknatisli-anahtar-ucu":
            variant["urun_tipi"] = "Manyetik lokma uç" if tr else "Магнитная торцевая головка"
        elif slug == "ph2-manyetik-bits-uc" and tr:
            variant["urun_tipi"] = "Manyetik bits uç"
        elif slug in ("duz-keski-sds-plus", "duz-keski-sds-max"):
            variant["urun_tipi"] = "Düz keski" if tr else "Плоское зубило"
            variant["baglanti_tipi"] = plus if slug.endswith("sds-plus") else max_
        elif slug in ("sivri-uclu-keski-murc-sds-plus", "sivri-uclu-keski-murc-sds-max"):
            variant["urun_tipi"] = "Sivri keski (murç)" if tr else "Пикообразное зубило"
            variant["baglanti_tipi"] = plus if slug.endswith("sds-plus") else max_


def apply_text(product: dict, name: str, description: str, features: list[str], applications: list[str], lang: str) -> None:
    old_name = product["name"]
    product["name"] = name
    product["description"] = description
    product["features"] = features
    product["applications"] = applications
    if old_name != name:
        for image in product.get("images") or []:
            alt = image.get("alt") or ""
            if alt.startswith(old_name):
                image["alt"] = name + alt[len(old_name) :]
    patch_labels(product["slug"], product.get("variants") or [], lang)


def apply_tr(catalog: dict, kaynak: dict) -> dict[str, tuple[str, str]]:
    by_src = {item["slug"]: item for item in kaynak["urunler"]}
    by_live = {item["slug"]: item for item in catalog["products"]}
    renamed: dict[str, tuple[str, str]] = {}
    for slug in TR_SLUGS:
        src = by_src[slug]
        targets = [slug, SIBLING[slug]] if slug in SIBLING else [slug]
        for target in targets:
            product = by_live[target]
            renamed[target] = (product["name"], product["description"])
            apply_text(product, src["name"], src["intro"], src["features"], src["applications"], "tr")
    return renamed


RU = {
    "cam-seramik-matkap-ucu": {
        "name": "Сверло по стеклу и керамике, четырёхрезцовое",
        "description": "Специально разработано для чистых и ровных отверстий без сколов, трещин и выкрашивания в керамике, плитке, керамограните, стекле, зеркалах и деликатных облицовочных материалах. Усиленная четырёхрезцовая крестообразная (пикообразная) твердосплавная алмазная геометрия полностью исключает увод в начале сверления и даёт точное центрование. Оптимизированный корпус снижает трение и нагрев и увеличивает ресурс сверла. Эффективно работает со стандартными патронами и аккумуляторными шуруповёртами.",
        "features": [
            "Четырёхрезцовая крестообразная твердосплавная головка снижает риск трещин и сколов на деликатных поверхностях",
            "Острая пикообразная геометрия облегчает точечное засверливание и не требует дополнительного кондуктора",
            "Специальная форма корпуса отводит тепло и облегчает выход стружки",
            "Ровное, без заусенцев и точно калиброванное отверстие даже на низких оборотах",
            "Хвостовик для быстрой смены сверла без проскальзывания",
        ],
        "applications": [
            "Сверление плоского стекла, некалёного стекла и зеркал",
            "Керамика, плитка и керамогранит мягкой и средней твёрдости",
            "Точное сверление настенной плитки при монтаже аксессуаров в ванной и на кухне",
            "Обработка керамики, черепицы и декоративной плитки",
        ],
    },
    "hss-matkap-ucu": {
        "name": "Сверло HSS по металлу",
        "description": "Сверло из высококачественной быстрорежущей стали HSS для быстрого, точного и безопасного сверления железа, стали, чугуна, алюминия и других металлических сплавов. Оптимизированный угол заточки предотвращает увод в начале сверления и формирует чистое отверстие без заусенцев. Высокая стойкость к нагреву и износу обеспечивает долгий ресурс в промышленной и профессиональной работе.",
        "features": [
            "Быстрорежущая сталь (HSS) для долгого ресурса и прочности",
            "Гладкая спиральная канавка ускоряет отвод стружки",
            "Специальное покрытие снижает трение и нагрев",
            "Точное центрование: лёгкий заход без предварительного кернения",
            "Полная совместимость со стандартными сверлильными патронами",
        ],
        "applications": [
            "Сверление легированной и нелегированной стали, чугуна и листового металла",
            "Обработка цветных металлов: алюминия, меди и латуни",
            "Промышленное производство, автосервис, металлообработка и сборочные цеха",
            "(Также показывает высокую производительность на твёрдом пластике и древесине)",
        ],
    },
    "sds-plus-2-kesicili-beton-matkap-ucu": {
        "name": "Двухрезцовый бур SDS Plus по бетону",
        "description": "Предназначен для высокопроизводительного ударного сверления бетона, кирпича и природного камня перфоратором. Корпус из высококачественной стали 40Х и закалённая двухрезцовая (алмазная) головка с напайкой твёрдого сплава ВК8 сохраняют стойкость в тяжёлых условиях. Бур изготовлен по стандарту Premium Quality и рассчитан на долгий ресурс (Long Life).",
        "features": [
            "Алмазная головка ВК8: острая кромка сразу входит в твёрдый материал и облегчает центрование.",
            "Корпус из стали 40Х: высокая ударная прочность и сплав, который гасит вибрацию и бережёт машину.",
            "Быстрый отвод пыли: расширенные спиральные канавки выносят пыль из отверстия и снижают износ и нагрев.",
            "Универсальная посадка: хвостовик совместим со всеми перфораторами SDS Plus (быстросъёмный патрон).",
            "Гарантия качества Premium: неограниченный срок хранения и высокая отдача на тяжёлой стройке.",
        ],
        "applications": [
            "Сверление обычного бетона, лёгкого бетона и газобетона (Ytong)",
            "Полнотелый и пустотелый кирпич, черепица и кладочные блоки",
            "Отверстия под дюбель и анкер в природном камне, известняке и песчанике",
            "Электромонтаж, водопровод, установка кондиционеров и общее крепление конструкций",
        ],
    },
    "sds-plus-4-kesicili-beton-matkap-ucu": {
        "name": "Четырёхрезцовый бур SDS Plus по бетону (Quadro)",
        "description": "Разработан для высокопроизводительного сверления самых твёрдых материалов: бетона, железобетона, природного камня, кирпича и стеновых блоков. Оптимизированная четырёхрезцовая геометрия Quadro (X-головка) снижает риск заклинивания и поломки при встрече с арматурой. Четыре спиральные канавки быстро выносят пыль и шлам, уменьшают нагрев и продлевают ресурс. Точное центрование даёт ровное, калиброванное отверстие без увода.",
        "features": [
            "Четырёхрезцовая головка Quadro не заклинивает и не ломается при встрече с арматурой в железобетоне",
            "Твердосплавная кромка с высокой стойкостью к износу",
            "Усиленные широкие четыре спиральные канавки максимально выносят пыль",
            "Полная совместимость со всеми перфораторами со стандартным патроном SDS Plus",
            "Баланс корпуса снижает вибрацию, повышает удобство и даёт точное центрование",
        ],
        "applications": [
            "Сверление бетона, железобетона (бетона с арматурой) и промышленных полов",
            "Природный камень, гранит, мрамор, кирпич, брикет и газобетонные блоки",
            "Точные отверстия под анкерный болт и дюбель",
            "Стройка, электромонтаж, инженерные сети и общий монтаж",
        ],
    },
    "sds-max-burc-aleti": {
        "name": "Бучарда SDS Max",
        "description": "Инструмент для шерохования бетонных, каменных и асфальтовых поверхностей, удаления старых покрытий и насечки. Высококачественные зубья из карбида вольфрама (алмаз) дают высокую производительность и долгий ресурс даже на особо твёрдом бетоне и природном камне. Полностью совместима с тяжёлыми перфораторами SDS MAX: снижает вибрацию и быстро шерохует широкие поверхности.",
        "features": [
            "Твердосплавные (алмазные) зубья с высокой стойкостью к износу",
            "Посадка SDS MAX с максимальной передачей усилия",
            "Стальной корпус, дополнительно усиленный против удара и излома",
            "Шероховатость, которая улучшает сцепление штукатурки и краски",
            "Быстрый съём материала при низком износе",
        ],
        "applications": [
            "Шерохование бетона, асфальта и природного камня",
            "Снятие старой штукатурки, краски, смолы и покрытий",
            "Насечка ступеней и полов против скольжения",
            "Промышленная подготовка поверхности и реставрация",
        ],
    },
    "miknatisli-anahtar-ucu": {
        "name": "Магнитная торцевая насадка",
        "description": "Высокопроизводительная магнитная насадка для затяжки гаек электрическим и аккумуляторным шуруповёртом. Изготовлена из особо прочной легированной стали CR40. Мощный внутренний магнит центрирует и крепко удерживает гайки и болты, не давая им упасть или соскользнуть. Надёжное, быстрое и удобное решение для монтажа с высоким крутящим моментом.",
        "features": [
            "Корпус из стали CR40 с высокой стойкостью к износу для тяжёлой работы",
            "Сильный магнит удерживает болт и гайку и позволяет работать одной рукой",
            "Конструкция держит высокий крутящий момент и не деформируется",
            "Стандартный шестигранный хвостовик 1/4\" точно садится в дрели и шуруповёрты",
            "Точная кромка не срывает головку винта",
        ],
        "applications": [
            "Монтаж профлиста, сэндвич-панелей и кровельных покрытий",
            "Стальные конструкции, фасады и строительные леса",
            "Автосервис, сборка машин и общие ремонтные мастерские",
            "Серийный монтаж саморезов с шестигранной головкой, специальных винтов и гаек",
        ],
    },
    "ph2-manyetik-bits-uc": {
        "name": "Магнитная бита PH2",
        "description": "Высокопроизводительная магнитная бита для интенсивной профессиональной работы с аккумуляторными и сетевыми шуруповёртами. Изготовлена из промышленной легированной стали S2+ и максимально стойка к износу, скручиванию и излому при высоком крутящем моменте. Сильный магнит крепко держит винт, не даёт ему соскользнуть и сохраняет форму головки. Несколько длин позволяют работать и в узких, труднодоступных местах.",
        "features": [
            "Гибкая и прочная инструментальная сталь S2+ для тяжёлой работы",
            "Сильный магнит центрирует винт и надёжно его удерживает",
            "Корпус рассчитан на высокий крутящий момент и ударную нагрузку",
            "Точно фрезерованный профиль PH2 (крест) плотно садится в головку винта",
            "Подходит ко всем стандартным битодержателям, аккумуляторным и сетевым шуруповёртам",
        ],
        "applications": [
            "Деревообработка, изготовление и сборка мебели",
            "Завинчивание в гипсокартон, ДСП и металлический профиль",
            "Автосервис, бытовая техника, ремонт и обслуживание машин",
            "Общестроительные, реставрационные и отделочные работы",
        ],
    },
    "duz-keski-sds-max": {
        "name": "Плоское зубило",
        "description": "Предназначено для долбления, скалывания и штробления бетона, кирпича, природного камня и асфальта. Высококачественная легированная сталь с термическим упрочнением стойка к излому и износу. Варианты хвостовика SDS Plus и SDS Max перекрывают работы от лёгкой реставрации до тяжёлого демонтажа. Зубило передаёт энергию перфоратора прямо на кромку и за счёт оптимизированного угла быстро и уверенно разрушает материал.",
        "features": [
            "Широкий ряд и для лёгкого долбления и реставрации (SDS Plus), и для тяжёлого демонтажа на объекте (SDS Max)",
            "Закалённая сталь с высокой ударной стойкостью против излома и скручивания",
            "Хвостовики без потери мощности, точно садящиеся в профессиональные перфораторы",
            "Геометрия корпуса снижает заклинивание в материале и вибрацию",
            "Специальное покрытие долго сохраняет форму режущей кромки",
        ],
        "applications": [
            "Общее долбление, скалывание и выравнивание бетона, камня, кирпича и подобных материалов",
            "Штробление стен и пола под электропроводку, воду и газ",
            "Съём старой плитки, керамики, остатков раствора, эпоксида и штукатурки",
            "Строительство, ремонт, реставрация и конструктивная доработка",
        ],
    },
    "sivri-uclu-keski-murc-sds-plus": {
        "name": "Пикообразное зубило",
        "description": "Усиленное пикообразное зубило для разрушения и тяжёлого демонтажа бетона, кирпича и природного камня. Высококачественная сталь даёт максимальное проникновение и стойкость к износу при интенсивной работе. Исполнения с хвостовиком SDS Plus и SDS Max передают энергию машины прямо на остриё и эффективны при точечном долблении.",
        "features": [
            "Усиленный пикообразный профиль для тяжёлого разрушения и долбления",
            "Стальной корпус с высокой ударной стойкостью против излома",
            "Оптимизированная форма быстро дробит твёрдый материал точечными ударами",
            "Промышленные хвостовики SDS Plus и SDS Max с минимальной потерей мощности",
            "Термообработка долго сохраняет форму острия",
        ],
        "applications": [
            "Долбление, разрушение и демонтаж стен из бетона, камня и кирпича",
            "Снятие стяжки, разрушение асфальта и твёрдых полов",
            "Подготовка фундамента, насечка и земляные работы",
            "Стройка, площадка, реставрация и тяжёлые конструктивные работы",
        ],
    },
}


def apply_ru(catalog: dict) -> dict[str, tuple[str, str]]:
    by_live = {item["slug"]: item for item in catalog["products"]}
    renamed: dict[str, tuple[str, str]] = {}
    for slug, copy in RU.items():
        targets = [slug, SIBLING[slug]] if slug in SIBLING else [slug]
        for target in targets:
            product = by_live[target]
            renamed[target] = (product["name"], product["description"])
            apply_text(product, copy["name"], copy["description"], copy["features"], copy["applications"], "ru")
    return renamed


def patch_meta(html: str, description: str) -> str:
    short = esc(description[:160])
    patterns = (
        r'(<meta name="description" content=")[^"]*(")',
        r'(<meta property="og:description" content=")[^"]*(")',
        r'(<meta name="twitter:description" content=")[^"]*(")',
    )
    for pattern in patterns:
        html = re.sub(pattern, rf"\1{short}\2", html, count=1)
    return html


def patch_jsonld(html: str, old_name: str, new_name: str, new_desc: str) -> str:
    def repl(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)

        def walk(node: object) -> None:
            if isinstance(node, dict):
                if node.get("@type") == "Product":
                    node["name"] = new_name
                    node["description"] = new_desc
                elif node.get("name") == old_name:
                    node["name"] = new_name
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(data)
        encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return f"{match.group(1)}{encoded}{match.group(3)}"

    return JSONLD_RE.sub(repl, html, count=1)


def patch_pages(folder: Path, renamed: dict[str, tuple[str, str]], catalog: dict) -> None:
    by_slug = {item["slug"]: item for item in catalog["products"]}
    for slug, (old_name, _old_desc) in renamed.items():
        path = folder / f"{slug}.html"
        product = by_slug[slug]
        html = path.read_text(encoding="utf-8")
        if old_name != product["name"]:
            html = html.replace(old_name, product["name"])
        html = patch_meta(html, product["description"])
        html = patch_jsonld(html, old_name, product["name"], product["description"])
        path.write_text(html, encoding="utf-8")
        print(f"html {path.relative_to(ROOT)}")


def main() -> None:
    kaynak = json.loads((ROOT / "data" / "katalog-kasim2026-icerik.json").read_text(encoding="utf-8"))
    tr_json = ROOT / "data" / "products.json"
    tr_js = ROOT / "assets" / "js" / "products-data.js"
    ru_json = ROOT / "ru" / "data" / "products-ru.json"
    ru_js = ROOT / "ru" / "assets" / "js" / "products-data-ru.js"

    tr = json.loads(tr_json.read_text(encoding="utf-8"))
    tr_renamed = apply_tr(tr, kaynak)
    write_json(tr_json, tr)
    prefix, js_catalog = load_js(tr_js)
    apply_tr(js_catalog, kaynak)
    write_js(tr_js, prefix, js_catalog)
    (ROOT / "products-data.js").write_text(tr_js.read_text(encoding="utf-8"), encoding="utf-8")

    ru = json.loads(ru_json.read_text(encoding="utf-8"))
    ru_renamed = apply_ru(ru)
    write_json(ru_json, ru)
    ru_prefix, ru_catalog = load_js(ru_js)
    apply_ru(ru_catalog)
    write_js(ru_js, ru_prefix, ru_catalog)

    patch_pages(ROOT / "urun", tr_renamed, js_catalog)
    patch_pages(ROOT / "ru" / "urun", ru_renamed, ru_catalog)
    print("catalog text applied")


if __name__ == "__main__":
    main()
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts" / "sync_catalog.py")], cwd=ROOT))
