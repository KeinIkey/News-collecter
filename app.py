import streamlit as st
import json
import os
from github import Github # PyGithub

st.set_page_config(page_title="Math Info Collector", layout="wide")

# GitHub連携設定 (設定保存のため)
# Streamlit CloudのSecretsから取得する前提
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN") 
REPO_NAME = "your-username/your-repo-name" # 後で書き換えてください

def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_config_to_github(topic, urls):
    if not GITHUB_TOKEN:
        st.error("GitHub Tokenが設定されていません。")
        return
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    # config.jsonの内容を作成
    new_config = {
        "topic": topic,
        "urls": [u.strip() for u in urls.split('\n') if u.strip()]
    }
    content = json.dumps(new_config, indent=2, ensure_ascii=False)
    
    # GitHub上のファイルを更新
    try:
        contents = repo.get_contents("config.json")
        repo.update_file(contents.path, "Update config via App", content, contents.sha)
        st.success("設定をGitHubに保存しました。次回の収集から反映されます。")
    except Exception as e:
        st.error(f"保存エラー: {e}")

# --- UI構築 ---

st.title("∫ Information Integrator")

tab1, tab2 = st.tabs(["収集レポート", "設定"])

with tab1:
    data = load_data()
    if not data:
        st.info("データが存在しません。収集処理が実行されるのを待つか、設定を確認してください。")
    
    for item in data:
        with st.expander(f"[{item['date']}] {item['title']}"):
            st.markdown(item['summary'])
            st.caption(f"Source: {item['source']} | [Link]({item['url']})")

with tab2:
    st.header("収集パラメータ設定")
    
    # 現在の設定を読み込み
    with open('config.json', 'r', encoding='utf-8') as f:
        current_config = json.load(f)
        
    new_topic = st.text_input("関心トピック", value=current_config.get('topic', ''))
    new_urls = st.text_area("対象URLリスト (改行区切り)", 
                            value='\n'.join(current_config.get('urls', [])))
    
    if st.button("設定を保存 (Commit to GitHub)"):
        save_config_to_github(new_topic, new_urls)
