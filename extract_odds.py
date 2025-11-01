import re
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

DATA_DIR = Path("..", "data")
HTML_DIR = DATA_DIR / "html"
TABLE_DIR = Path("..", "data", "table")
PLACE_MAPPING = {
    1: "札幌",
    2: "函館",
    3: "福島",
    4: "新潟",
    5: "東京",
    6: "中山",
    7: "中京",
    8: "京都",
    9: "阪神",
    10: "小倉",
}
# サイト上の馬券種名とキーの対応付け
BET_TYPE_MAPPING = {
    "単勝・複勝": "tanpuku",
    "枠連": "wakuren",
    "馬連": "umaren",
    "ワイド": "wide",
    "馬単": "umatan",
    "3連複": "sanrenpuku",
    "連複": "sanrenpuku",  # 表記揺れに対応
    "3連単": "sanrentan",
    "連単": "sanrentan",  # 表記揺れに対応
}


class RealtimeOdds:
    """
    実際の購入時に使用するオッズを取得するためのクラス。
    """

    def __init__(
        self,
        race_id: str,
    ):
        self.race_id = race_id
        self.htmls = {}

    async def scrape_html(
        self,
        skip_bet_types: list[str] = ["wakuren", "wide"],
        headless: bool = True,
        delay_time: int = 1000,
    ) -> None:
        """
        レースIDを指定してJRA公式サイトからオッズページのHTMLを取得する関数。

        Parameters
        --------
        skip_bet_types : list[str], optional
            スキップする馬券種のリスト。デフォルトは["wakuren", "wide"]
        headless : bool, optional
            ブラウザをヘッドレスモードで実行するかどうか。デフォルトはTrue
        delay_time : int, optional
            ページ遷移時の遅延時間（ミリ秒）。デフォルトは1000

        Returns
        --------
        None
            結果はインスタンス変数 self.htmls に辞書形式で格納される。
        """
        async with async_playwright() as playwright:
            kaisai_name = (
                f"{int(self.race_id[6:8])}回"
                + f"{PLACE_MAPPING[int(self.race_id[4:6])]}"
                + f"{int(self.race_id[8:10])}日"
            )
            race_name = f"{int(self.race_id[10:12])}レース"
            browser = await playwright.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await page.goto("https://www.jra.go.jp/keiba/")
                await page.get_by_role("link", name="オッズ", exact=True).click(
                    delay=delay_time
                )
                await page.wait_for_load_state("domcontentloaded")
                kaisai_link = page.get_by_role("link", name=kaisai_name)
                if await kaisai_link.count() > 0:
                    await kaisai_link.click(delay=delay_time)
                    await page.get_by_role("link", name=race_name, exact=True).click(
                        delay=delay_time
                    )
                else:
                    # オッズページにリンクが存在しない場合、レース結果ページから遷移させる
                    await page.get_by_role("link", name="レース結果").click(
                        delay=delay_time
                    )
                    await page.get_by_role("link", name=kaisai_name).click(
                        delay=delay_time
                    )
                    await page.get_by_role("link", name=race_name, exact=True).click(
                        delay=delay_time
                    )
                    await page.locator("#race_result").get_by_role(
                        "link", name="オッズ"
                    ).click(delay=delay_time)
                nav_pills = page.locator("ul.nav.pills")
                await page.wait_for_load_state("domcontentloaded")
                bet_type_items = nav_pills.locator("li")
                for i in range(await bet_type_items.count()):
                    bet_item = bet_type_items.nth(i)
                    bet_link = bet_item.locator("a")
                    bet_type_name = await bet_link.inner_text()
                    bet_type = BET_TYPE_MAPPING[bet_type_name]
                    if bet_type in skip_bet_types:
                        continue
                    await bet_link.click()
                    await page.wait_for_load_state("domcontentloaded")
                    html = await page.content()
                    self.htmls[bet_type] = html
            finally:
                await context.close()
                await browser.close()

    def extract_tansho(self) -> None:
        """
        単勝オッズのHTMLを解析し、{馬番: オッズ}の辞書をself.tanshoに保存する。
        self.htmls["tanpuku"]に保存されたHTMLを解析対象とする。
        """
        if "tanpuku" not in self.htmls:
            print(f"警告: extract_tansho - self.htmlsに'tanpuku'キーが存在しません。")
            print(f"利用可能なキー: {list(self.htmls.keys())}")
            self.tansho = {}
            return
        
        soup = BeautifulSoup(self.htmls["tanpuku"], "lxml")
        # 単勝・複勝オッズテーブルを取得
        odds_table = soup.select_one("table.tanpuku")
        if not odds_table:
            print(f"警告: extract_tansho - table.tanpukuが見つかりませんでした。")
            self.tansho = {}
            return
        
        # テーブルの行を取得
        rows = odds_table.select("tbody tr")
        odds_data = {}
        for row in rows:
            # 馬番を取得
            umaban_elem = row.select_one("td.num")
            if not umaban_elem:
                print(f"No <td.num>")
                continue
            umaban = umaban_elem.text.strip()
            # 単勝オッズを取得
            tan_odds_elem = row.select_one("td.odds_tan")
            if not tan_odds_elem:
                print(f"No <td.odds_tan>")
                continue
            tan_odds = tan_odds_elem.text.strip().replace(",", "")
            try:
                odds_data[int(umaban)] = float(tan_odds)
            except ValueError:
                pass
        self.tansho = odds_data
        print(f"情報: extract_tansho - 単勝オッズを{len(odds_data)}件取得しました。")

    def extract_fukusho(self) -> None:
        """
        複勝オッズのHTMLを解析し、{馬番: オッズ下限}の辞書をself.fukushoに保存する。
        self.htmls["tanpuku"]に保存されたHTMLを解析対象とする。
        複勝オッズは範囲（下限・上限）があるため、下限（最小値）を取得する。
        """
        if "tanpuku" not in self.htmls:
            print(f"警告: extract_fukusho - self.htmlsに'tanpuku'キーが存在しません。")
            print(f"利用可能なキー: {list(self.htmls.keys())}")
            self.fukusho = {}
            return
        
        soup = BeautifulSoup(self.htmls["tanpuku"], "lxml")
        # 単勝・複勝オッズテーブルを取得
        odds_table = soup.select_one("table.tanpuku")
        if not odds_table:
            print(f"警告: extract_fukusho - table.tanpukuが見つかりませんでした。")
            self.fukusho = {}
            return
        
        # テーブルの行を取得
        rows = odds_table.select("tbody tr")
        odds_data = {}
        
        # デバッグ用: 最初の行のtd要素のクラス名を確認
        if rows:
            first_row = rows[0]
            all_tds = first_row.select("td")
            td_classes = [td.get("class", []) for td in all_tds]
            print(f"デバッグ: extract_fukusho - 最初の行のtdクラス: {td_classes}")
        
        for row in rows:
            # 馬番を取得
            umaban_elem = row.select_one("td.num")
            if not umaban_elem:
                print(f"警告: extract_fukusho - <td.num>が見つかりませんでした。")
                continue
            umaban = umaban_elem.text.strip()
            
            # 複勝オッズを取得（複数の可能性のあるクラス名を試す）
            fuku_odds_elem = None
            
            # 複数の可能性のあるクラス名を試す（td.odds_fukuを優先）
            possible_classes = [
                "td.odds_fuku",  # 最も一般的なクラス名
                "td.odds_fukusho",
                "td.odds_fuku1",
                "td.odds_fuku2",
                "td.odds_fuku3",
            ]
            
            for class_name in possible_classes:
                fuku_odds_elem = row.select_one(class_name)
                if fuku_odds_elem:
                    break
            
            # 上記のクラス名で見つからない場合、td要素を順に確認
            if not fuku_odds_elem:
                all_tds = row.select("td")
                for td in all_tds:
                    td_class = td.get("class", [])
                    # odds_fukuを含むクラス名を探す
                    if any("fuku" in str(c).lower() for c in td_class):
                        fuku_odds_elem = td
                        break
                    # または、単勝オッズの後に来るtd要素を確認
                    # (単勝オッズがodds_tanの場合、その次のtdが複勝オッズの可能性)
            
            # 最後の手段1: 単勝オッズのtdの次のtd要素を確認
            if not fuku_odds_elem:
                tan_odds_elem = row.select_one("td.odds_tan")
                if tan_odds_elem:
                    # 単勝オッズのtdの次の兄弟要素（td）を取得
                    next_td = tan_odds_elem.find_next_sibling("td")
                    if next_td:
                        # 単勝オッズのクラス名ではないことを確認
                        next_td_class = next_td.get("class", [])
                        if "odds_tan" not in str(next_td_class).lower():
                            fuku_odds_elem = next_td
            
            # 最後の手段2: td要素のインデックスで判断（単勝オッズの次のtd）
            if not fuku_odds_elem:
                all_tds = row.select("td")
                tan_odds_idx = None
                for idx, td in enumerate(all_tds):
                    if "odds_tan" in str(td.get("class", [])).lower():
                        tan_odds_idx = idx
                        break
                if tan_odds_idx is not None and tan_odds_idx + 1 < len(all_tds):
                    next_td = all_tds[tan_odds_idx + 1]
                    # 単勝オッズのクラス名ではないことを確認
                    next_td_class = next_td.get("class", [])
                    if "odds_tan" not in str(next_td_class).lower():
                        fuku_odds_elem = next_td
            
            if not fuku_odds_elem:
                # デバッグ出力: この行のすべてのtd要素を確認
                all_tds = row.select("td")
                td_info = [
                    {
                        "class": td.get("class", []),
                        "text": td.text.strip()[:20],
                    }
                    for td in all_tds
                ]
                print(f"警告: extract_fukusho - 馬番{umaban}の複勝オッズtdが見つかりません。td情報: {td_info}")
                continue
            
            # 複勝オッズの下限（最小値）を取得（span.minから）
            min_odds_span = fuku_odds_elem.select_one("span.min")
            if not min_odds_span:
                print(f"警告: extract_fukusho - 馬番{umaban}の<span.min>が見つかりませんでした。")
                continue
            
            fuku_odds_low = min_odds_span.text.strip().replace(",", "")
            try:
                # 複勝オッズの下限（最小値）を取得
                odds_data[int(umaban)] = float(fuku_odds_low)
            except ValueError as e:
                print(f"警告: extract_fukusho - 馬番{umaban}の複勝オッズ下限変換エラー: {fuku_odds_low}, エラー: {e}")
                pass
        
        self.fukusho = odds_data
        print(f"情報: extract_fukusho - 複勝オッズを{len(odds_data)}件取得しました。")

    def extract_umaren(self) -> None:
        """
        馬連オッズのHTMLを解析し、{馬番の組み合わせ: オッズ}の辞書をself.umarenに保存する。
        self.htmls["umaren"]に保存されたHTMLを解析対象とする。
        """
        if "umaren" not in self.htmls:
            print(f"警告: extract_umaren - self.htmlsに'umaren'キーが存在しません。")
            print(f"利用可能なキー: {list(self.htmls.keys())}")
            self.umaren = {}
            return
        
        soup = BeautifulSoup(self.htmls["umaren"], "lxml")
        odds_data = {}
        list_blocks = soup.select("ul.umaren_list")
        for list_block in list_blocks:
            table_elements = list_block.select("li")
            for table_element in table_elements:
                # テーブルのキャプションから第一馬番を取得
                caption = table_element.select_one("caption")
                if not caption:
                    print(f"No <caption>")
                    continue
                first_horse = caption.text.strip()
                rows = table_element.select("tbody tr")
                for row in rows:
                    second_horse_elem = row.select_one("th")
                    if not second_horse_elem:
                        print(f"No <th>")
                        continue
                    second_horse = second_horse_elem.text.strip()
                    odds_td = row.select_one("td")
                    if not odds_td:
                        print(f"No <td>")
                        continue
                    odds_text = odds_td.text.strip().replace(",", "")
                    kumi = f"{first_horse.zfill(2)},{second_horse.zfill(2)}"
                    try:
                        odds_data[kumi] = float(odds_text)
                    except ValueError:
                        pass
        self.umaren = odds_data

    def extract_umatan(self) -> None:
        """
        馬単オッズのHTMLを解析し、{馬番の組み合わせ: オッズ}の辞書をself.umatanに保存する。
        self.htmls["umatan"]に保存されたHTMLを解析対象とする。
        """
        soup = BeautifulSoup(self.htmls["umatan"], "lxml")
        odds_data = {}
        list_blocks = soup.select("ul.umatan_list")
        for list_block in list_blocks:
            table_elements = list_block.select("li")
            for table_element in table_elements:
                # テーブルのキャプションから1着馬番を取得
                caption = table_element.select_one("caption")
                if not caption:
                    print(f"No <caption>")
                    continue
                first_horse = caption.text.strip()
                rows = table_element.select("tbody tr")
                for row in rows:
                    second_horse_element = row.select_one("th")
                    if not second_horse_element:
                        print(f"No <th>")
                        continue
                    second_horse = second_horse_element.text.strip()
                    odds_td = row.select_one("td")
                    if not odds_td:
                        print(f"No <td>")
                        continue
                    odds_text = odds_td.text.strip().replace(",", "")
                    # 組み合わせの作成（2桁,2桁の形式）
                    kumi = f"{first_horse.zfill(2)},{second_horse.zfill(2)}"
                    try:
                        odds_data[kumi] = float(odds_text)
                    except ValueError:
                        pass
        self.umatan = odds_data

    def extract_sanrenpuku(self) -> None:
        """
        3連複オッズのHTMLを解析し、{馬番の組み合わせ: オッズ}の辞書をself.sanrenpukuに保存する。
        self.htmls["sanrenpuku"]に保存されたHTMLを解析対象とする。
        """
        soup = BeautifulSoup(self.htmls["sanrenpuku"], "lxml")
        odds_data = {}
        fuku3_units = soup.select("div.fuku3_unit")
        for unit in fuku3_units:
            # 1頭目の馬番を取得
            first_horse_elem = unit.select_one("h4 span.inner span.num")
            if not first_horse_elem:
                print(f"No <span.num>")
                continue
            first_horse = first_horse_elem.text.strip()
            list_blocks = unit.select("ul.fuku3_list")
            for list_block in list_blocks:
                list_items = list_block.select("li")
                for item in list_items:
                    # 2頭目の馬番を取得
                    caption = item.select_one("table caption")
                    if not caption:
                        print(f"No <caption>")
                        continue
                    caption_text = caption.text
                    second_horse_match = re.search(r"(\d+)-(\d+)", caption_text)
                    if not second_horse_match:
                        print(f"No match")
                        continue
                    second_horse = second_horse_match.group(2)
                    rows = item.select("table tbody tr")
                    for row in rows:
                        # 3頭目の馬番を取得
                        third_horse_elem = row.select_one("th")
                        if not third_horse_elem:
                            print(f"No <th>")
                            continue
                        third_horse = third_horse_elem.text.strip()
                        # オッズを取得
                        odds_td = row.select_one("td")
                        if not odds_td:
                            print(f"No <td>")
                            continue
                        odds_text = odds_td.text.strip().replace(",", "")
                        # 組み合わせの作成（2桁,2桁,2桁の形式）
                        kumi = f"{first_horse.zfill(2)},{second_horse.zfill(2)},{third_horse.zfill(2)}"
                        try:
                            odds_data[kumi] = float(odds_text)
                        except ValueError:
                            pass
        self.sanrenpuku = odds_data

    def extract_sanrentan(self) -> None:
        """
        3連単オッズのHTMLを解析し、{馬番の組み合わせ: オッズ}の辞書をself.sanrentanに保存する。
        self.htmls["sanrentan"]に保存されたHTMLを解析対象とする。
        """
        soup = BeautifulSoup(self.htmls["sanrentan"], "lxml")
        odds_data = {}
        tan3_units = soup.select("div.tan3_unit")
        for unit in tan3_units:
            # 1着馬の番号を取得
            first_horse_elem = unit.select_one("span.num")
            if not first_horse_elem:
                print(f"No <span.num>")
                continue
            first_horse = first_horse_elem.text.strip()
            list_blocks = unit.select("ul.tan3_list")
            for list_block in list_blocks:
                list_items = list_block.select("li")
                for item in list_items:
                    # 2着馬の番号を取得
                    second_horse_elem = item.select_one(
                        "div.p_line:nth-of-type(2) div.num"
                    )
                    if not second_horse_elem:
                        print(f"No <div.num>")
                        continue
                    second_horse = second_horse_elem.text.strip()
                    rows = item.select("table.tan3 tbody tr")
                    for row in rows:
                        # 3着馬の番号を取得
                        third_horse_elem = row.select_one("th")
                        if not third_horse_elem:
                            print(f"No <th>")
                            continue
                        third_horse = third_horse_elem.text.strip()
                        # オッズ値を取得
                        odds_td = row.select_one("td")
                        if not odds_td:
                            print(f"No <td>")
                            continue
                        odds_text = odds_td.text.strip().replace(",", "")
                        kumi = f"{first_horse.zfill(2)},{second_horse.zfill(2)},{third_horse.zfill(2)}"
                        try:
                            odds_data[kumi] = float(odds_text)
                        except ValueError:
                            pass
        self.sanrentan = odds_data
