import streamlit as st
import collections
import pandas as pd

# --- ロジック部分 (変更なし) ---
def combine_classes(class_durations):
    """
    90分授業を45分×2に分割し、できるだけ異なる教科同士を組み合わせるロジック
    """
    pool = []
    for subject, count in class_durations.items():
        pool.extend([subject] * (count * 2))
    
    counts = collections.Counter(pool)
    pairs = []
    
    while sum(counts.values()) > 0:
        sorted_subjects = counts.most_common()
        
        primary = sorted_subjects[0][0]
        counts[primary] -= 1
        
        secondary = None
        if len(sorted_subjects) > 1 and sorted_subjects[1][1] > 0:
            secondary = sorted_subjects[1][0]
            counts[secondary] -= 1
        else:
            if counts[primary] > 0:
                 secondary = primary
                 counts[primary] -= 1
            else:
                 secondary = "空き時間"

        pair = tuple(sorted([primary, secondary]))
        pairs.append(pair)
    
    return pairs

# --- スタイリング (CSS注入) ---
def inject_custom_css():
    st.markdown("""
    <style>
    /* メインコンテナの余白調整（スマホ向け） */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* カード風デザイン */
    .lesson-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b; /* アクセントカラー */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .lesson-card.safe {
        border-left: 5px solid #00c853; /* OKなときは緑 */
        background-color: #e8f5e9;
    }
    .card-title {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.5em;
        display: flex;
        align-items: center;
        justify_content: space-between;
    }
    .card-badge {
        background-color: #ffffff;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        color: #555;
        border: 1px solid #ddd;
    }
    /* ボタンのスタイル */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Webアプリの画面部分 ---
def main():
    st.set_page_config(page_title="時間割メーカー", page_icon="📅", layout="centered")
    inject_custom_css() # CSSを適用

    st.title("📅 時間割メーカー")
    st.caption("スマホ対応・90分授業分割ツール")
    
    # --- サイドバー (入力) ---
    with st.sidebar:
        st.header("📝 設定")
        st.write("各教科のコマ数(90分)を入力")
        
        subjects = ["国語", "算数", "英語", "理科", "社会"]
        input_data = {}
        
        # グリッドレイアウトで入力をコンパクトに（スマホだと縦に並びます）
        for subject in subjects:
            input_data[subject] = st.number_input(
                f"{subject}", 
                min_value=0, max_value=20, value=1, step=1
            )
        
        st.write("---")
        calc_btn = st.button("組み合わせを作成 ✨", type="primary")

    # --- メインエリア ---
    if sum(input_data.values()) == 0:
        st.info("👈 サイドバー（左上の > ボタン）から教科のコマ数を入力してください。")
        # デモ用のグラフを表示しておく（見た目の賑やかし）
        st.subheader("📊 現在のバランス")
        df_demo = pd.DataFrame({"コマ数": [0]*5}, index=subjects)
        st.bar_chart(df_demo)
        return

    # グラフの表示（入力状況の可視化）
    st.subheader("📊 入力バランス")
    chart_data = pd.DataFrame.from_dict(input_data, orient='index', columns=['コマ数'])
    st.bar_chart(chart_data)

    if calc_btn:
        # ロジック実行
        results = combine_classes(input_data)
        pair_counts = collections.Counter(results)
        
        st.divider()
        st.subheader(f"✅ 作成結果 (全{len(results)}枠)")
        
        # スマホで見やすいようにカード形式でループ表示
        for pair, count in pair_counts.items():
            subject1, subject2 = pair
            is_same = subject1 == subject2
            
            # アイコンとクラス分け
            if is_same:
                css_class = "lesson-card" # デフォルト（赤アクセント）
                icon = "⚠️"
                status_text = "同じ教科ペア"
            else:
                css_class = "lesson-card safe" # 安全（緑アクセント）
                icon = "✨"
                status_text = "Good!"

            # HTMLを使ってカードを描画
            st.markdown(f"""
            <div class="{css_class}">
                <div class="card-title">
                    <span>{icon} {subject1} ＋ {subject2}</span>
                    <span class="card-badge">{count}コマ</span>
                </div>
                <div style="font-size: 0.9em; color: #666;">
                    {status_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 最終メッセージ
        has_warning = any(p[0] == p[1] for p in pair_counts.keys())
        if has_warning:
            st.warning("一部、コマ数が偏っているため同じ教科のペアが発生しました。")
        else:
            st.success("全てのコマが良いバランスで組み合わされました！")

if __name__ == "__main__":
    main()
