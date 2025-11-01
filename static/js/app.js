/**
 * JRAレースオッズ表示ツール - フロントエンド
 * 
 * 機能:
 * - race_idの入力と検証
 * - APIからオッズ情報を取得
 * - グリッド形式でオッズを表示
 * - クリップボードにコピー
 */

// レースIDをURLから抽出する関数
function extractRaceIdFromUrl(url) {
    // race_idパラメータを抽出
    const match = url.match(/race_id=(\d+)/);
    if (match) {
        return match[1];
    }
    
    // URLがrace_idそのものの場合（数字のみ）
    if (/^\d+$/.test(url.trim())) {
        return url.trim();
    }
    
    return null;
}

// 馬連の組み合わせをフォーマット（小さい数字-大きい数字、ゼロ埋めなし）
function formatUmarenKumi(horse1, horse2) {
    const smaller = Math.min(horse1, horse2);
    const larger = Math.max(horse1, horse2);
    return `${smaller}-${larger}`;
}

// 馬連の上位2つを取得し、共通する馬番を軸とする関数
function getUmarenTopPopular(umarenOdds) {
    if (!umarenOdds || Object.keys(umarenOdds).length < 2) {
        return { topTwo: [], axisHorse: null };
    }
    
    // 馬連オッズを全てオッズ順にソート
    const umarenSorted = Object.entries(umarenOdds)
        .map(([kumi, odds]) => {
            const horses = kumi.split(',').map(h => parseInt(h.trim()));
            return { kumi, odds, horses };
        })
        .sort((a, b) => a.odds - b.odds);
    
    if (umarenSorted.length < 2) {
        return { topTwo: [], axisHorse: null };
    }
    
    // 上位2つを取得
    const topTwo = umarenSorted.slice(0, 2);
    
    // 2つの組み合わせに共通して含まれる馬番を探す
    const firstComboHorses = new Set(topTwo[0].horses);
    const secondComboHorses = new Set(topTwo[1].horses);
    const commonHorses = [...firstComboHorses].filter(h => secondComboHorses.has(h));
    
    // 軸馬番を決定
    let axisHorse = null;
    if (commonHorses.length > 0) {
        axisHorse = commonHorses[0];
    } else {
        axisHorse = topTwo[0].horses[0];
    }
    
    return { topTwo, axisHorse };
}

// データをTSV形式に変換
function convertToTSV(data) {
    const rows = [];
    
    // 各行を追加
    for (const [label, values] of Object.entries(data)) {
        const row = [label, ...values].join('\t');
        rows.push(row);
    }
    
    return rows.join('\n');
}

// オッズ情報を表示用データに変換
function prepareDisplayData(tanshoOdds, fukushoOdds, umarenOdds) {
    const displayData = {};
    
    // 単勝_オッズ行と単勝_馬番行（単勝オッズの低い順にソート）
    if (tanshoOdds && Object.keys(tanshoOdds).length > 0) {
        const tanshoSorted = Object.entries(tanshoOdds)
            .sort((a, b) => a[1] - b[1]);
        
        displayData['単勝_オッズ'] = tanshoSorted.map(([, odds]) => odds.toFixed(2));
        displayData['単勝_馬番'] = tanshoSorted.map(([horse]) => parseInt(horse).toString().padStart(2, '0'));
    } else {
        displayData['単勝_オッズ'] = [];
        displayData['単勝_馬番'] = [];
    }
    
    // 複勝_オッズ行と複勝_馬番行（複勝オッズの低い順にソート）
    if (fukushoOdds && Object.keys(fukushoOdds).length > 0) {
        const fukushoSorted = Object.entries(fukushoOdds)
            .sort((a, b) => a[1] - b[1]);
        
        displayData['複勝_オッズ'] = fukushoSorted.map(([, odds]) => odds.toFixed(2));
        displayData['複勝_馬番'] = fukushoSorted.map(([horse]) => parseInt(horse).toString().padStart(2, '0'));
    } else {
        displayData['複勝_オッズ'] = [];
        displayData['複勝_馬番'] = [];
    }
    
    // 馬連_オッズ行と馬連_馬番行（馬連上位2つを先頭に入れる）
    const { topTwo, axisHorse } = getUmarenTopPopular(umarenOdds);
    const umarenRow = [];
    const umarenHorsesRow = [];
    
    if (topTwo.length >= 2 && axisHorse !== null) {
        // 馬連上位2つを先頭に追加
        for (const combo of topTwo) {
            const formattedKumi = formatUmarenKumi(combo.horses[0], combo.horses[1]);
            umarenRow.push(combo.odds.toFixed(2));
            umarenHorsesRow.push(formattedKumi);
        }
        
        // 軸馬番を含む相手馬番をオッズの低い順に追加（上位2つは除外）
        const topTwoKumi = new Set(topTwo.map(c => {
            const formatted = formatUmarenKumi(c.horses[0], c.horses[1]);
            return formatted;
        }));
        
        // 軸馬番を含む全ての馬連オッズを抽出
        const axisUmarenOdds = Object.entries(umarenOdds)
            .map(([kumi, odds]) => {
                const horses = kumi.split(',').map(h => parseInt(h.trim()));
                if (horses.includes(axisHorse)) {
                    const formatted = formatUmarenKumi(horses[0], horses[1]);
                    return { formatted, odds };
                }
                return null;
            })
            .filter(item => item !== null && !topTwoKumi.has(item.formatted))
            .sort((a, b) => a.odds - b.odds);
        
        for (const item of axisUmarenOdds) {
            umarenRow.push(item.odds.toFixed(2));
            umarenHorsesRow.push(item.formatted);
        }
    }
    
    displayData['馬連_オッズ'] = umarenRow;
    displayData['馬連_馬番'] = umarenHorsesRow;
    
    // 最大列数を取得
    const maxCols = Math.max(
        ...Object.values(displayData).map(row => row.length)
    );
    
    // 各行の長さを揃える（不足分は空文字で埋める）
    for (const key in displayData) {
        while (displayData[key].length < maxCols) {
            displayData[key].push('');
        }
    }
    
    return { displayData, maxCols, topTwo, axisHorse };
}

// テーブルを表示
function displayOddsTable(displayData, maxCols) {
    const container = document.getElementById('odds-table-container');
    container.innerHTML = '';
    
    const table = document.createElement('table');
    table.className = 'odds-table';
    
    // ヘッダー行
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // 左端のラベル列
    const labelHeader = document.createElement('th');
    labelHeader.textContent = '';
    headerRow.appendChild(labelHeader);
    
    // データ列のヘッダー（順位番号）
    for (let i = 0; i < maxCols; i++) {
        const th = document.createElement('th');
        th.textContent = (i + 1).toString().padStart(2, '0');
        headerRow.appendChild(th);
    }
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // データ行
    const tbody = document.createElement('tbody');
    for (const [label, values] of Object.entries(displayData)) {
        const row = document.createElement('tr');
        
        // ラベル列
        const labelCell = document.createElement('td');
        labelCell.textContent = label;
        row.appendChild(labelCell);
        
        // データ列
        for (let i = 0; i < maxCols; i++) {
            const cell = document.createElement('td');
            cell.textContent = values[i] || '';
            row.appendChild(cell);
        }
        
        tbody.appendChild(row);
    }
    
    table.appendChild(tbody);
    container.appendChild(table);
}

// オッズ情報を取得
async function fetchOdds(raceId) {
    const response = await fetch(`/api/odds?race_id=${raceId}`);
    const result = await response.json();
    
    if (!result.success) {
        throw new Error(result.error || 'オッズ情報の取得に失敗しました');
    }
    
    return result.data;
}

// メイン処理
document.addEventListener('DOMContentLoaded', () => {
    const fetchBtn = document.getElementById('fetch-btn');
    const raceInput = document.getElementById('race-input');
    const loadingSection = document.getElementById('loading-section');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    const resultsSection = document.getElementById('results-section');
    const copyBtn = document.getElementById('copy-btn');
    const infoSection = document.getElementById('info-section');
    
    let currentDisplayData = null;
    
    // オッズ取得ボタンのクリック
    fetchBtn.addEventListener('click', async () => {
        const inputValue = raceInput.value.trim();
        
        if (!inputValue) {
            alert('URLまたはrace_idを入力してください。');
            return;
        }
        
        // race_idを抽出
        const raceId = extractRaceIdFromUrl(inputValue);
        
        if (!raceId) {
            alert('race_idを抽出できませんでした。正しいURLまたはrace_idを入力してください。');
            return;
        }
        
        // UIの更新
        loadingSection.style.display = 'block';
        errorSection.style.display = 'none';
        resultsSection.style.display = 'none';
        fetchBtn.disabled = true;
        
        try {
            // オッズ情報を取得
            const oddsData = await fetchOdds(raceId);
            
            // 表示用データに変換
            const { displayData, maxCols, topTwo, axisHorse } = prepareDisplayData(
                oddsData.tansho,
                oddsData.fukusho,
                oddsData.umaren
            );
            
            // テーブルを表示
            displayOddsTable(displayData, maxCols);
            
            // 情報セクションを更新
            if (topTwo.length >= 2 && axisHorse !== null) {
                const combo1 = topTwo[0];
                const combo2 = topTwo[1];
                const formatted1 = formatUmarenKumi(combo1.horses[0], combo1.horses[1]);
                const formatted2 = formatUmarenKumi(combo2.horses[0], combo2.horses[1]);
                
                infoSection.innerHTML = `
                    <div class="info-section">
                        <p>馬連上位2つ: ${formatted1}（${combo1.odds.toFixed(2)}）、${formatted2}（${combo2.odds.toFixed(2)}） | 軸: ${axisHorse.toString().padStart(2, '0')}番</p>
                    </div>
                `;
            }
            
            // 結果を表示
            currentDisplayData = displayData;
            resultsSection.style.display = 'block';
            
        } catch (error) {
            errorMessage.textContent = `エラーが発生しました: ${error.message}`;
            errorSection.style.display = 'block';
        } finally {
            loadingSection.style.display = 'none';
            fetchBtn.disabled = false;
        }
    });
    
    // コピーボタンのクリック
    copyBtn.addEventListener('click', () => {
        if (!currentDisplayData) {
            return;
        }
        
        const tsvData = convertToTSV(currentDisplayData);
        
        navigator.clipboard.writeText(tsvData).then(() => {
            // コピー成功（メッセージなし）
        }).catch(err => {
            alert('コピーに失敗しました: ' + err);
        });
    });
});

