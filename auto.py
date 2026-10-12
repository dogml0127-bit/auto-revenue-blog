import os
import datetime
import re
import random
import subprocess
import google.generativeai as genai

# 1. API 키 설정
MY_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=MY_API_KEY)

def clean_ai_traces(text):
    cleaned_lines = []
    for line in text.split('\n'):
        if re.search(r'[a-zA-Z]', line) and not line.startswith('#'):
            continue
        line = line.replace("오늘 이 글에서는", "").replace("이런", "").replace("결론적으로", "")
        cleaned_lines.append(line)
    
    joined_text = '\n'.join(cleaned_lines)
    if '#' in joined_text:
        joined_text = joined_text[joined_text.find('#'):]
    return joined_text.strip()

def generate_perfect_korean_content():
    prompt = """
    당신은 자기계발 및 성장을 주제로 독립 블로그를 운영하는 진솔한 블로거입니다.
    오늘 날짜와 무작위 영감에 기반하여 '일상의 깨달음, 생산성 향상, 혹은 마인드셋 변화'에 대한 완전히 새로운 주제를 스스로 선정하십시오.

    [작성 스타일 및 톤앤매너]
    1. 과도하게 친한 척하거나 대화체("들어봐", "친구야")를 절대 사용하지 마십시오.
    2. 철저히 1인칭 시점("저", "제가", "~했습니다", "~하게 되었습니다")으로 작성하십시오.
    3. 본인이 일상에서 직접 경험하고 느낀 바를 담담하게 기록하는 '성찰형 에세이' 톤을 유지하십시오.
    4. 본문은 번호가 매겨진 소제목(## 1. ~하다)을 사용하여 논리적으로 정리하십시오.

    [절대 규칙 - 위반 시 실패]
    1. 첫 글자는 반드시 '#'으로 시작하는 제목이어야 합니다. 그 전에는 어떤 말도 하지 마십시오.
    2. 모든 문장은 반드시 한국어(한글)로만 작성하십시오. (영어 알파벳 사용 완전 금지)
    3. 분량은 최소 2,000자 이상으로 길고 상세하게 작성하십시오.
    """

    print("🔍 영감을 탐색하여 새로운 블로그 포스팅을 창작합니다...")
    
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        for model_name in available_models:
            try:
                clean_model_name = model_name.replace("models/", "")
                print(f"   ▶ [{clean_model_name}] 모델 시도 중...")
                
                model = genai.GenerativeModel(clean_model_name)
                response = model.generate_content(prompt)
                
                if response.text:
                    perfect_text = clean_ai_traces(response.text)
                    if len(perfect_text) > 100: 
                        print(f"   🌟 SUCCESS! 고품질 포스팅 작성을 완료했습니다!")
                        return perfect_text
                    
            except Exception:
                continue 
    except Exception as e:
        print(f"🚨 시스템 에러: {e}")

    return "# 일상의 쉼표\n\n오늘은 생각을 정리하기 위해 잠시 쉬어갑니다."

def push_to_github(file_path):
    """생성된 파일을 GitHub 저장소로 자동 커밋 및 푸시하는 함수"""
    print("🌐 GitHub 저장소로 자동 업로드를 시작합니다...")
    try:
        # Git 명령어 순차 실행
        subprocess.run(["git", "add", file_path], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", f"Auto-post: {datetime.date.today()} 콘텐츠 업로드"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "push"], check=True, stdout=subprocess.DEVNULL)
        print("✅ GitHub 업로드 완벽 성공! 블로그가 곧 자동으로 업데이트됩니다.")
    except subprocess.CalledProcessError as e:
        print("⚠️ 아직 Git 저장소가 연결되지 않았거나 변경 사항이 없습니다. 먼저 GitHub 세팅이 필요합니다.")

if __name__ == "__main__":
    generated_text = generate_perfect_korean_content()
    
    # 1. 로컬 posts 폴더에 저장 (정적 블로그 구조에 맞춤)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    os.makedirs("posts", exist_ok=True)
    file_name = f"posts/{today_str}-insight.md"
    
    with open(file_name, "w", encoding="utf-8") as f:
        # 대부분의 정적 블로그(Jekyll/Hugo 등)가 인식하는 머리말(Front-matter)
        front_matter = f"---\nlayout: post\ntitle: '오늘의 기록'\ndate: {today_str}\ncategories: ['마인드셋']\n---\n\n"
        f.write(front_matter + generated_text)
    
    print(f"💾 마크다운 파일 생성 완료: {file_name}")
    
    # 2. GitHub으로 자동 푸시
    push_to_github(file_name)