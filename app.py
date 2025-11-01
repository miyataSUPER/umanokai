"""
Streamlitアプリケーション: JRAレースオッズ表示ツール

概要:
    netkeibaのURLまたはrace_idを入力し、そのレースの単勝・複勝オッズ、
    および単勝一番人気軸の馬連オッズを表示する。

主な機能:
    - netkeibaのURLまたはrace_idを受け取る
    - JRA公式サイトからオッズ情報を取得
    - 単勝・複勝オッズを表示
    - 単勝一番人気軸の馬連オッズを表示

制限事項:
    - JRA公式サイトのHTML構造に依存しているため、サイト構造が変更されると動作しない可能性がある
    - 非同期処理が必要なため、実行に時間がかかる場合がある
"""

import re
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from extract_odds import RealtimeOdds


def ensure_playwright_chromium():
    """
    PlaywrightのChromiumがインストールされているか確認し、
    インストールされていない場合は自動的にインストールする。
    
    Streamlit Cloud無料版でInstall commandが設定できない場合の対処法。
    """
    # 既にインストール済みとマークされている場合はスキップ
    if st.session_state.get("chromium_installed", False):
        return True
    
    try:
        from playwright.sync_api import sync_playwright
        
        # Playwrightのインスタンスを作成して、Chromiumが存在するかチェック
        with sync_playwright() as p:
            try:
                # Chromiumを起動してみる（存在する場合は成功）
                browser = p.chromium.launch(headless=True)
                browser.close()
                # インストール済みとマーク
                st.session_state.chromium_installed = True
                return True
            except Exception as e:
                # Chromiumがインストールされていない場合
                if not st.session_state.get("chromium_installing", False):
                    st.session_state.chromium_installing = True
                    st.info("🔧 Chromiumをインストール中です。初回のみ時間がかかります...")
                    
                    # subprocessでplaywright install chromiumを実行
                    result = subprocess.run(
                        [sys.executable, "-m", "playwright", "install", "chromium"],
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5分のタイムアウト
                    )
                    if result.returncode == 0:
                        # システム依存関係もインストール（sudo権限が必要な場合があるため、スキップしても良い）
                        # Streamlit Cloudでは、packages.txtを使ってシステム依存関係をインストールする
                        try:
                            subprocess.run(
                                [sys.executable, "-m", "playwright", "install-deps", "chromium"],
                                capture_output=True,
                                text=True,
                                timeout=180,  # 3分のタイムアウト
                            )
                        except Exception as deps_error:
                            # 依存関係のインストールに失敗しても続行
                            st.warning(f"⚠️ システム依存関係のインストールで警告がありました（続行します）: {str(deps_error)}")
                        st.session_state.chromium_installing = False
                        st.success("✅ Chromiumのインストールが完了しました。")
                        # インストール完了をマークして、メインアプリを表示できるようにする
                        # 実際の動作確認は次回のアクセス時に行う
                        st.session_state.chromium_installed = True
                        st.info("ℹ️ インストールが完了しました。アプリが使用可能になりました。")
                        st.rerun()
                        return True
                    else:
                        st.session_state.chromium_installing = False
                        st.error(f"❌ Chromiumのインストールに失敗しました: {result.stderr}")
                        return False
                else:
                    # インストール中なので待機
                    st.info("⏳ Chromiumのインストールを続行しています...")
                    return False
    except Exception as e:
        # エラーが発生した場合、スキップして続行を試みる
        st.warning(f"⚠️ Chromiumの確認中にエラーが発生しました: {str(e)}")
        st.info("⚠️ 初回実行時は、Streamlit CloudのログでChromiumのインストール状況を確認してください。")
        # エラーが発生しても、続行を試みる
        st.session_state.chromium_installed = True
        return False


# アプリ起動時にChromiumのインストールを確認
chromium_ready = ensure_playwright_chromium()

# インストール中またはインストール失敗の場合は、メインアプリを表示しない
if st.session_state.get("chromium_installing", False):
    st.stop()  # インストール中の場合は処理を停止


def format_umaren_kumi(horse1: int, horse2: int) -> str:
    """
    馬連の組み合わせをフォーマットする。
    
    小さい馬番を先頭に、ハイフンで区切り、ゼロ埋めなしで表記する。
    例: (1, 15) -> "1-15", (5, 10) -> "5-10", (15, 1) -> "1-15"
    
    Parameters
    ----------
    horse1 : int
        馬番1
    horse2 : int
        馬番2
    
    Returns
    -------
    str
        フォーマットされた組み合わせ（例: "1-15"）
    """
    smaller = min(horse1, horse2)
    larger = max(horse1, horse2)
    return f"{smaller}-{larger}"


def extract_race_id_from_url(url: str) -> Optional[str]:
    """
    netkeibaのURLからrace_idを抽出する。
    
    対応するURL形式:
    - https://race.netkeiba.com/race/shutuba.html?race_id=202505041007
    - https://race.netkeiba.com/race/result.html?race_id=202508031009&rf=race_list
    - 202505041007 (race_idそのもの)

    Parameters
    ----------
    url : str
        netkeibaのURLまたはrace_id

    Returns
    -------
    Optional[str]
        抽出されたrace_id。抽出できない場合はNoneを返す。
    """
    # race_idパラメータを抽出（shutuba.html、result.htmlなどに対応）
    match = re.search(r"race_id=(\d+)", url)
    if match:
        return match.group(1)
    
    # URLがrace_idそのものの場合（数字のみ）
    if re.match(r"^\d+$", url.strip()):
        return url.strip()
    
    return None


def convert_netkeiba_race_id_to_jra(race_id: str) -> Optional[str]:
    """
    netkeiba形式のrace_idをJRA形式のrace_idに変換する。

    Parameters
    ----------
    race_id : str
        netkeiba形式のrace_id（例: 202505041007）

    Returns
    -------
    Optional[str]
        JRA形式のrace_id。変換できない場合はNoneを返す。

    Note
    ----
    netkeiba形式: YYYYMMDDプラスコード（12桁）
        - 例: 202505041007
        - YYYY: 2025（年）
        - MM: 05（月）
        - DD: 04（日）
        - プラスコード: 1（1桁、競馬場コードと関連）
        - レース番号: 007（3桁）
    
    JRA形式: 12桁（仮想）
        - 構造はJRA公式サイトの実装に依存するため、
          実際の形式に合わせて調整が必要
        - 現在はnetkeiba形式をそのまま使用（テスト用）
    """
    if len(race_id) != 12:
        return None
    
    # 数字のみかチェック
    if not race_id.isdigit():
        return None
    
    # netkeiba形式のrace_idを解析
    # 例: 202505041007
    date_part = race_id[:8]  # 20250504
    place_code = race_id[8]  # 1（競馬場コードの可能性）
    race_number_str = race_id[9:]  # 007
    
    # レース番号を数値に変換（先頭の0を除去して2桁にする）
    try:
        race_number_int = int(race_number_str)
        race_number = f"{race_number_int:02d}"  # 2桁に変換
    except ValueError:
        return None
    
    # JRA形式への変換（実際の形式に合わせて調整が必要）
    # 現在はnetkeiba形式のrace_idをそのまま使用
    # （実際のJRA公式サイトのrace_id形式が異なる場合は、変換ロジックを追加）
    # TODO: JRA公式サイトのrace_id形式を確認し、正確な変換ロジックを実装する
    
    return race_id


async def fetch_odds(race_id: str) -> dict:
    """
    指定されたrace_idのオッズ情報を取得する。

    Parameters
    ----------
    race_id : str
        JRA形式のrace_id

    Returns
    -------
    dict
        オッズ情報を含む辞書。キーは 'tansho', 'fukusho', 'umaren', 'error'
    """
    try:
        # RealtimeOddsインスタンスを作成
        odds_extractor = RealtimeOdds(race_id)
        
        # HTMLを取得（単勝・複勝、馬連を含む）
        # Streamlit Cloud無料版用に最適化: delay_timeを短縮し、メモリ使用量を削減
        await odds_extractor.scrape_html(
            skip_bet_types=["wakuren", "wide", "umatan", "sanrenpuku", "sanrentan"],
            headless=True,
            delay_time=300,  # Streamlit Cloud無料版用に短縮
        )
        
        # 単勝オッズを抽出
        odds_extractor.extract_tansho()
        
        # 複勝オッズを抽出
        odds_extractor.extract_fukusho()
        
        # 馬連オッズを抽出
        odds_extractor.extract_umaren()
        
        return {
            "tansho": getattr(odds_extractor, "tansho", {}),
            "fukusho": getattr(odds_extractor, "fukusho", {}),
            "umaren": getattr(odds_extractor, "umaren", {}),
            "error": None,
        }
    except Exception as e:
        return {
            "tansho": {},
            "fukusho": {},
            "umaren": {},
            "error": str(e),
        }


def get_umaren_top_popular(
    tansho_odds: dict, umaren_odds: dict
) -> tuple[list, Optional[int], pd.DataFrame]:
    """
    馬連の上位人気2つを取得し、その2つに共通して含まれる馬番を軸として取得する。
    
    処理手順:
        1. 馬連オッズを全てオッズ順にソート
        2. 上位2つを取得
        3. その2つの組み合わせに共通して含まれる馬番を軸とする
        4. 軸を含む全ての馬連オッズを返す
    
    Parameters
    ----------
    tansho_odds : dict
        単勝オッズの辞書（{馬番: オッズ}）
    umaren_odds : dict
        馬連オッズの辞書（{組み合わせ: オッズ}）
    
    Returns
    -------
    tuple[list, Optional[int], pd.DataFrame]
        (馬連上位2つの組み合わせ情報のリスト, 軸馬番, 軸馬番を含む馬連オッズのDataFrame)
        上位2つが見つからない場合は (空リスト, None, empty DataFrame)
    """
    if not umaren_odds:
        return [], None, pd.DataFrame(columns=["軸馬番", "相手馬番", "組み合わせ", "オッズ"])
    
    # 馬連オッズを全てオッズ順にソート
    umaren_sorted = sorted(umaren_odds.items(), key=lambda x: x[1])
    
    if len(umaren_sorted) < 2:
        return [], None, pd.DataFrame(columns=["軸馬番", "相手馬番", "組み合わせ", "オッズ"])
    
    # 上位2つを取得
    top_two = umaren_sorted[:2]
    top_two_combinations = []
    for kumi, odds in top_two:
        # 組み合わせの形式は "01,05" のような形式
        horses = [int(h.strip()) for h in kumi.split(",")]
        # 新しい表記形式に変換（小さい数字を先頭、ハイフン区切り、ゼロ埋めなし）
        formatted_kumi = format_umaren_kumi(horses[0], horses[1])
        top_two_combinations.append({
            "組み合わせ": formatted_kumi,
            "オッズ": odds,
            "馬番1": horses[0],
            "馬番2": horses[1],
        })
    
    # 2つの組み合わせに共通して含まれる馬番を探す
    first_combo_horses = {top_two_combinations[0]["馬番1"], top_two_combinations[0]["馬番2"]}
    second_combo_horses = {top_two_combinations[1]["馬番1"], top_two_combinations[1]["馬番2"]}
    
    # 共通の馬番を取得
    common_horses = first_combo_horses & second_combo_horses
    
    if not common_horses:
        # 共通の馬番がない場合は、上位1つ目の組み合わせの1番目の馬番を軸とする
        axis_horse = top_two_combinations[0]["馬番1"]
    else:
        # 共通の馬番がある場合、その中から1つを軸とする（最初のもの）
        axis_horse = list(common_horses)[0]
    
    # 軸馬番を含む全ての馬連オッズを抽出
    axis_umaren_odds = []
    for kumi, odds in umaren_odds.items():
        # 組み合わせの形式は "02,05" のような形式
        horses = [int(h.strip()) for h in kumi.split(",")]
        # 軸馬番が含まれているかチェック
        if axis_horse in horses:
            # もう一頭の馬番を取得
            other_horse = horses[1] if horses[0] == axis_horse else horses[0]
            # 新しい表記形式に変換（小さい数字を先頭、ハイフン区切り、ゼロ埋めなし）
            formatted_kumi = format_umaren_kumi(horses[0], horses[1])
            axis_umaren_odds.append({
                "軸馬番": axis_horse,
                "相手馬番": other_horse,
                "組み合わせ": formatted_kumi,
                "オッズ": odds,
            })
    
    # デバッグ: 軸馬番を含む全ての組み合わせを確認
    print(f"デバッグ: 軸馬番{axis_horse}を含む組み合わせ数: {len(axis_umaren_odds)}")
    print(f"デバッグ: 全ての組み合わせ: {[combo['相手馬番'] for combo in axis_umaren_odds]}")
    
    if not axis_umaren_odds:
        return top_two_combinations, axis_horse, pd.DataFrame(columns=["軸馬番", "相手馬番", "組み合わせ", "オッズ"])
    
    # DataFrameに変換
    df = pd.DataFrame(axis_umaren_odds)
    # オッズでソート
    df = df.sort_values("オッズ")
    
    return top_two_combinations, axis_horse, df


def main():
    """
    Streamlitアプリケーションのメイン関数。
    """
    st.title("🏇 JRAレースオッズ表示ツール")
    st.markdown("---")
    
    # 入力セクション
    st.header("📥 入力")
    input_value = st.text_input(
        "netkeibaのURLまたはrace_idを入力してください",
        placeholder="例: https://race.netkeiba.com/race/shutuba.html?race_id=202505041007 または 202505041007",
    )
    
    if st.button("オッズを取得", type="primary"):
        if not input_value:
            st.error("URLまたはrace_idを入力してください。")
            return
        
        # race_idを抽出
        race_id = extract_race_id_from_url(input_value)
        
        if not race_id:
            st.error("race_idを抽出できませんでした。正しいURLまたはrace_idを入力してください。")
            return
        
        # JRA形式に変換（必要に応じて）
        jra_race_id = convert_netkeiba_race_id_to_jra(race_id)
        
        if not jra_race_id:
            st.error("JRA形式のrace_idに変換できませんでした。")
            return
        
        st.info(f"取得中のrace_id: {jra_race_id}")
        
        # プログレスバーを表示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("オッズ情報を取得しています...")
        progress_bar.progress(30)
        
        # オッズを取得（非同期処理を実行）
        try:
            odds_data = asyncio.run(fetch_odds(jra_race_id))
            progress_bar.progress(100)
            
            if odds_data["error"]:
                st.error(f"エラーが発生しました: {odds_data['error']}")
                return
            
            # オッズ情報を表示（横一列グリッド形式）
            st.header("📊 オッズ情報")
            
            # データの整理
            tansho_odds = odds_data["tansho"]
            fukusho_odds = odds_data["fukusho"]
            umaren_odds = odds_data["umaren"]
            
            # 単勝オッズを低い順にソート（馬番とオッズのペア）
            if tansho_odds:
                tansho_sorted = sorted(tansho_odds.items(), key=lambda x: x[1])
                tansho_horses = [horse for horse, _ in tansho_sorted]
                tansho_values = [odds for _, odds in tansho_sorted]
            else:
                tansho_sorted = []
                tansho_horses = []
                tansho_values = []
            
            # 複勝オッズを低い順にソート（馬番とオッズのペア）
            if fukusho_odds:
                fukusho_sorted = sorted(fukusho_odds.items(), key=lambda x: x[1])
                fukusho_horses = [horse for horse, _ in fukusho_sorted]
                fukusho_values = [odds for _, odds in fukusho_sorted]
            else:
                fukusho_sorted = []
                fukusho_horses = []
                fukusho_values = []
            
            # 馬連の上位人気2つを取得し、共通する馬番を軸とする
            top_two_umaren = []
            axis_horse = None
            axis_umaren_df = pd.DataFrame()
            if umaren_odds:
                top_two_umaren, axis_horse, axis_umaren_df = get_umaren_top_popular(
                    tansho_odds, umaren_odds
                )
            
            if not tansho_odds and not fukusho_odds and axis_umaren_df.empty:
                st.warning("オッズデータが見つかりませんでした。")
                return
            
            # 各行ごとにオッズ順にソートしてデータを準備
            display_data = {}
            
            # 単勝_オッズ行と単勝_馬番行（単勝オッズの低い順にソート）
            if tansho_odds:
                # 単勝オッズの低い順にソート
                tansho_sorted_for_display = sorted(tansho_odds.items(), key=lambda x: x[1])
                
                # 単勝_オッズ行
                tansho_row = []
                # 単勝_馬番行
                tansho_horses_row = []
                
                for idx, (horse, odds) in enumerate(tansho_sorted_for_display):
                    tansho_row.append(f"{odds:.2f}")
                    tansho_horses_row.append(str(horse))  # 一桁の数字も一桁で出力（ゼロ埋めなし）
                
                display_data["単勝_オッズ"] = tansho_row
                display_data["単勝_馬番"] = tansho_horses_row
            else:
                display_data["単勝_オッズ"] = []
                display_data["単勝_馬番"] = []
            
            # 複勝_オッズ行と複勝_馬番行（複勝オッズの低い順にソート）
            if fukusho_odds:
                # 複勝オッズの低い順にソート
                fukusho_sorted_for_display = sorted(fukusho_odds.items(), key=lambda x: x[1])
                
                # 複勝_オッズ行
                fukusho_row = []
                # 複勝_馬番行
                fukusho_horses_row = []
                
                for idx, (horse, odds) in enumerate(fukusho_sorted_for_display):
                    fukusho_row.append(f"{odds:.2f}")
                    fukusho_horses_row.append(str(horse))  # 一桁の数字も一桁で出力（ゼロ埋めなし）
                
                display_data["複勝_オッズ"] = fukusho_row
                display_data["複勝_馬番"] = fukusho_horses_row
            else:
                display_data["複勝_オッズ"] = []
                display_data["複勝_馬番"] = []
            
            
            # 馬連_オッズ行と馬連_馬番行（新しい形式：先頭に軸馬番のみ、次に相手馬番のみ）
            if axis_horse is not None and not axis_umaren_df.empty:
                umaren_odds_row = []
                umaren_horses_row = []
                
                # 軸馬番を含む全ての組み合わせを取得（オッズ順にソート済み）
                # axis_umaren_dfには軸馬番を含む全ての組み合わせが含まれているはず
                sorted_combinations = []
                for _, row in axis_umaren_df.iterrows():
                    sorted_combinations.append({
                        "相手馬番": int(row['相手馬番']),  # 整数型に変換
                        "オッズ": row['オッズ'],
                    })
                
                # 相手馬番でソート（オッズ順が既に保たれているが、念のため確認）
                # オッズ順に既にソートされているはずだが、念のため再ソート
                sorted_combinations = sorted(sorted_combinations, key=lambda x: x['オッズ'])
                
                if len(sorted_combinations) >= 3:
                    # 先頭には軸馬番のみ（数字のみ、記号なし）
                    umaren_horses_row.append(str(axis_horse))
                    
                    # 先頭のオッズは、2番目と3番目の組み合わせから「相手馬番同士の組み合わせ」のオッズを探す
                    # 例: 2番目が6-10、3番目が6-9の場合、9-10のオッズを先頭に入れる
                    first_other_horse = sorted_combinations[1]["相手馬番"]  # 2番目の相手馬番（インデックス1）
                    second_other_horse = sorted_combinations[2]["相手馬番"]  # 3番目の相手馬番（インデックス2）
                    
                    # 小さい方を先頭にした組み合わせを探す
                    smaller = min(first_other_horse, second_other_horse)
                    larger = max(first_other_horse, second_other_horse)
                    
                    # umaren_oddsから該当する組み合わせのオッズを探す
                    first_odds = None
                    for kumi, odds in umaren_odds.items():
                        horses = [int(h.strip()) for h in kumi.split(",")]
                        if (horses[0] == smaller and horses[1] == larger) or (horses[1] == smaller and horses[0] == larger):
                            first_odds = odds
                            break
                    
                    # 見つからない場合は、2番目のオッズを使用
                    if first_odds is None:
                        first_odds = sorted_combinations[1]["オッズ"]
                    
                    umaren_odds_row.append(f"{first_odds:.2f}")
                    
                    # 全ての組み合わせを表示（1番目から全て）
                    for combo in sorted_combinations:  # 全ての組み合わせ
                        umaren_odds_row.append(f"{combo['オッズ']:.2f}")
                        umaren_horses_row.append(str(combo['相手馬番']))
                elif len(sorted_combinations) >= 2:
                    # 組み合わせが2つしかない場合（先頭のオッズは2番目のオッズを使用）
                    umaren_horses_row.append(str(axis_horse))
                    umaren_odds_row.append(f"{sorted_combinations[1]['オッズ']:.2f}")
                    # 全ての組み合わせを表示
                    for combo in sorted_combinations:
                        umaren_odds_row.append(f"{combo['オッズ']:.2f}")
                        umaren_horses_row.append(str(combo['相手馬番']))
                elif len(sorted_combinations) == 1:
                    # 組み合わせが1つだけの場合
                    umaren_horses_row.append(str(axis_horse))
                    umaren_odds_row.append(f"{sorted_combinations[0]['オッズ']:.2f}")
                    umaren_horses_row.append(str(sorted_combinations[0]['相手馬番']))
                else:
                    # 組み合わせがない場合
                    umaren_horses_row.append(str(axis_horse))
                
                display_data["馬連_オッズ"] = umaren_odds_row
                display_data["馬連_馬番"] = umaren_horses_row
            else:
                display_data["馬連_オッズ"] = []
                display_data["馬連_馬番"] = []
            
            # 最大の列数を取得（全ての行の長さを確認）
            max_cols = max(
                [len(display_data.get(key, [])) for key in display_data],
                default=0,
            )
            
            if max_cols == 0:
                st.warning("オッズデータが見つかりませんでした。")
                return
            
            # 馬連の表示形式変更により、各行の長さが一致するようになったため、
            # 空白で埋める処理は不要になりました
            # （各行の長さが異なる場合は、そのまま表示します）
            
            # DataFrameを作成（行名がラベル、列は順番）
            # display_dataは辞書で、キーが行名、値がリスト（列データ）になっている
            # これを転置して、行がラベル、列がデータになるようにする
            display_df = pd.DataFrame.from_dict(display_data, orient='index')
            
            # 実際の列数を確認（DataFrame作成後の実際の列数）
            actual_cols = len(display_df.columns)
            
            # 列名を1から始まる連番に設定（順位を表す）
            if actual_cols > 0:
                display_df.columns = [f"{i+1:02d}" for i in range(actual_cols)]
            
            # 行名を保持（左端のラベル列として表示される）
            display_df.index.name = None
            
            # カスタムスタイルで表示
            st.markdown("### オッズ一覧表（オッズ順ソート）")
            if not display_df.empty:
                # インデックスを表示（左端のラベル列）
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=200,
                )
                st.caption("※各列はオッズの低い順（人気順）に並んでいます")
                
                # クリップボードにコピーするボタン
                # データをTSV形式（タブ区切り）に変換（ヘッダーなし）
                tsv_data = display_df.to_csv(sep='\t', index=True, header=False)
                
                # TSVデータをJSON文字列としてエスケープ（安全に扱うため）
                tsv_data_json = json.dumps(tsv_data)
                
                # HTMLとJavaScriptでクリップボードコピー機能を実装
                copy_button_html = f"""
                <script>
                function copyToClipboard() {{
                    const data = {tsv_data_json};
                    navigator.clipboard.writeText(data).then(function() {{
                        // メッセージなしでコピー完了
                    }}, function(err) {{
                        alert('コピーに失敗しました: ' + err);
                    }});
                }}
                </script>
                <button onclick="copyToClipboard()" style="
                    background-color: #1f77b4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    margin-top: 10px;
                ">📋 データをクリップボードにコピー</button>
                """
                components.html(copy_button_html, height=50)
                
            else:
                st.warning("表示するデータがありません。")
            
            # 馬連上位2つと軸情報の表示
            if len(top_two_umaren) >= 2 and axis_horse is not None:
                combo1 = top_two_umaren[0]
                combo2 = top_two_umaren[1]
                st.info(
                    f"馬連上位2つ: {combo1['組み合わせ']}（{combo1['オッズ']:.2f}）、"
                    f"{combo2['組み合わせ']}（{combo2['オッズ']:.2f}） | "
                    f"軸: {axis_horse:02d}番"
                )
            
            status_text.text("✅ オッズ情報の取得が完了しました。")
            
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()

