import re
import os

# 템플릿 읽기
with open(r'C:\Users\master\monsmecta_landing\public\assets\labels\monsmecta_label_print_v2_modern.html', 'r', encoding='utf-8') as f:
    template = f.read()

# 기존 라벨에서 추출한 정확한 성분 정보
products = [
    {
        'file': 'hepamax',
        'kor_name': '헤파맥스',
        'eng_name': 'HEPAMAX',
        'color_primary': 'D4AF37',
        'color_secondary': 'F0D060',
        'color_bg1': 'FFFDF5',
        'color_bg2': 'FFF9E6',
        'color_bg3': 'FFF3D1',
        'text_color': '3A2F1A',
        'sub_text': '5A4A2B',
        'accent_color': '8B6D1E',
        'icon_color1': 'FFF8E1',
        'icon_color2': 'FFF3D1',
        'icon_color3': 'FFE8B3',
        'icon_color4': 'FFDF99',
        'badge': '간건강',
        'desc': '간 기능 개선 및 해독에 뛰어난',
        # 기존 성분 (hepamax_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 비타민A, 아세트산나트륨, 프로피온산나트륨, 포도당, 몬모릴로나이트, 타우린, D-소르비톨, L-라이신, L-메티오닌, 비타민B12, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        # 효능 (간 관련)
        'eff1': '간 보호',
        'eff1_sub': '기능 개선',
        'eff2': '해독',
        'eff2_sub': '독소 배출',
        'eff3': '대사',
        'eff3_sub': '촉진 작용',
        'eff4': '회복',
        'eff4_sub': '피로 개선',
    },
    {
        'file': 'jointcare',
        'kor_name': '조인트케어',
        'eng_name': 'JOINTCARE',
        'color_primary': '84CC16',
        'color_secondary': 'BEF264',
        'color_bg1': 'F7FEE7',
        'color_bg2': 'ECFCCB',
        'color_bg3': 'D9F99D',
        'text_color': '1A2E05',
        'sub_text': '3F6212',
        'accent_color': '4D7C0F',
        'icon_color1': 'ECFCCB',
        'icon_color2': 'D9F99D',
        'icon_color3': 'BEF264',
        'icon_color4': 'A3E635',
        'badge': '관절건강',
        'desc': '관절 및 연골 건강에 뛰어난',
        # 기존 성분 (jointcare_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, MSM, 그린립 머슬 추출물, 보스웰리아, 콘드로이친, 오메가3, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '관절',
        'eff1_sub': '윤활 작용',
        'eff2': '연골',
        'eff2_sub': '보호·재생',
        'eff3': '염증',
        'eff3_sub': '완화 작용',
        'eff4': '활동',
        'eff4_sub': '기동성 향상',
    },
    {
        'file': 'skincare',
        'kor_name': '스킨케어',
        'eng_name': 'SKINCARE',
        'color_primary': 'EC4899',
        'color_secondary': 'F9A8D4',
        'color_bg1': 'FDF2F8',
        'color_bg2': 'FCE7F3',
        'color_bg3': 'FBCFE8',
        'text_color': '500F2D',
        'sub_text': '831843',
        'accent_color': 'BE185D',
        'icon_color1': 'FCE7F3',
        'icon_color2': 'FBCFE8',
        'icon_color3': 'F9A8D4',
        'icon_color4': 'F472B6',
        'badge': '피부건강',
        'desc': '피부와 털 건강에 뛰어난',
        # 기존 성분 (skincare_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 퀘르세틴, 브로멜라인, 오메가3, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '피부',
        'eff1_sub': '보습·진정',
        'eff2': '털',
        'eff2_sub': '윤기·탄력',
        'eff3': '재생',
        'eff3_sub': '상처 회복',
        'eff4': '염증',
        'eff4_sub': '알러지 완화',
    },
    {
        'file': 'heartcare',
        'kor_name': '하트케어',
        'eng_name': 'HEARTCARE',
        'color_primary': 'EF4444',
        'color_secondary': 'FCA5A5',
        'color_bg1': 'FEF2F2',
        'color_bg2': 'FEE2E2',
        'color_bg3': 'FECACA',
        'text_color': '450A0A',
        'sub_text': '7F1D1D',
        'accent_color': 'B91C1C',
        'icon_color1': 'FEE2E2',
        'icon_color2': 'FECACA',
        'icon_color3': 'FCA5A5',
        'icon_color4': 'F87171',
        'badge': '심장건강',
        'desc': '심장 기능 및 혈액순환에 뛰어난',
        # 기존 성분 (heartcare_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 코큐텐(Q10), 산사나무 열매 추출물, L-카르니틴, 타우린, 오메가3, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '심장',
        'eff1_sub': '기능 강화',
        'eff2': '혈액',
        'eff2_sub': '순환 개선',
        'eff3': '에너지',
        'eff3_sub': '생산 촉진',
        'eff4': '항산화',
        'eff4_sub': '세포 보호',
    },
    {
        'file': 'urinary',
        'kor_name': '유리너리',
        'eng_name': 'URINARY',
        'color_primary': '6366F1',
        'color_secondary': 'A5B4FC',
        'color_bg1': 'EEF2FF',
        'color_bg2': 'E0E7FF',
        'color_bg3': 'C7D2FE',
        'text_color': '1E1B4B',
        'sub_text': '312E81',
        'accent_color': '4338CA',
        'icon_color1': 'E0E7FF',
        'icon_color2': 'C7D2FE',
        'icon_color3': 'A5B4FC',
        'icon_color4': '818CF8',
        'badge': '비뇨기건강',
        'desc': '비뇨기 및 요로 건강에 뛰어난',
        # 기존 성분 (urinary_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 아세트산나트륨, 프로피온산나트륨, 포도당, 몬모릴로나이트, 비타민A, 비타민D3, 비타민E, 비타민B1, 비타민B2, 비타민C, 니코틴산아미드, 판토텐산 칼슘, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '요로',
        'eff1_sub': '세균 억제',
        'eff2': '방광',
        'eff2_sub': '점막 보호',
        'eff3': '결석',
        'eff3_sub': '예방 작용',
        'eff4': '배뇨',
        'eff4_sub': '기능 개선',
    },
    {
        'file': 'probiotics',
        'kor_name': '프로바이오틱스',
        'eng_name': 'PROBIOTICS',
        'color_primary': '14B8A6',
        'color_secondary': '5EEAD4',
        'color_bg1': 'F0FDFA',
        'color_bg2': 'CCFBF1',
        'color_bg3': '99F6E4',
        'text_color': '042F2E',
        'sub_text': '115E59',
        'accent_color': '0F766E',
        'icon_color1': 'CCFBF1',
        'icon_color2': '99F6E4',
        'icon_color3': '5EEAD4',
        'icon_color4': '2DD4BF',
        'badge': '장건강',
        'desc': '장내 미생물 균형에 뛰어난',
        # 기존 성분 (probiotics_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 비타민A, 아세트산나트륨, 프로피온산나트륨, 포도당, 몬모릴로나이트, 듀퐁 다니스코 특화 유산균(L. plantarum 등 18종), 프락토올리고당, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '정장',
        'eff1_sub': '유익균 증식',
        'eff2': '소화',
        'eff2_sub': '흡수 개선',
        'eff3': '면역',
        'eff3_sub': '장내면역',
        'eff4': '배변',
        'eff4_sub': '활동 개선',
    },
    {
        'file': 'vitaplus',
        'kor_name': '비타플러스',
        'eng_name': 'VITAPLUS',
        'color_primary': 'EAB308',
        'color_secondary': 'FDE047',
        'color_bg1': 'FEFCE8',
        'color_bg2': 'FEF9C3',
        'color_bg3': 'FEF08A',
        'text_color': '3A2A1A',
        'sub_text': 'A16207',
        'accent_color': 'A16207',
        'icon_color1': 'FEF9C3',
        'icon_color2': 'FEF08A',
        'icon_color3': 'FDE047',
        'icon_color4': 'FACC15',
        'badge': '종합비타민',
        'desc': '종합 비타민 및 미네랄 보충에 뛰어난',
        # 기존 성분 (vitaplus_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 아세트산나트륨, 프로피온산나트륨, 포도당, 몬모릴로나이트, 비타민A, 비타민D3, 비타민E, L-메티오닌, L-아르기닌, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '비타민',
        'eff1_sub': '종합 보충',
        'eff2': '미네랄',
        'eff2_sub': '균형 공급',
        'eff3': '에너지',
        'eff3_sub': '대사 촉진',
        'eff4': '항산화',
        'eff4_sub': '노화 방지',
    },
    {
        'file': 'coldzero',
        'kor_name': '콜드제로',
        'eng_name': 'COLDZERO',
        'color_primary': '06B6D4',
        'color_secondary': '67E8F9',
        'color_bg1': 'ECFEFF',
        'color_bg2': 'CFFAFE',
        'color_bg3': 'A5F3FC',
        'text_color': '3A2A1A',
        'sub_text': '0E7490',
        'accent_color': '0E7490',
        'icon_color1': 'CFFAFE',
        'icon_color2': 'A5F3FC',
        'icon_color3': '67E8F9',
        'icon_color4': '22D3EE',
        'badge': '감기케어',
        'desc': '감기 및 호흡기 건강에 뛰어난',
        # 기존 성분 (coldzero_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 퀘르세틴, 맥문동추출물, 유근피추출물, 쌍화복합추출물, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '감기',
        'eff1_sub': '예방·완화',
        'eff2': '호흡기',
        'eff2_sub': '점막 보호',
        'eff3': '면역',
        'eff3_sub': '기능 강화',
        'eff4': '회복',
        'eff4_sub': '빠른 쾌유',
    },
    {
        'file': 'powerase',
        'kor_name': '파워라제',
        'eng_name': 'POWERASE',
        'color_primary': 'F97316',
        'color_secondary': 'FDBA74',
        'color_bg1': 'FFF7ED',
        'color_bg2': 'FFEDD5',
        'color_bg3': 'FED7AA',
        'text_color': '3A2A1A',
        'sub_text': 'C2410C',
        'accent_color': 'C2410C',
        'icon_color1': 'FFEDD5',
        'icon_color2': 'FED7AA',
        'icon_color3': 'FDBA74',
        'icon_color4': 'FB923C',
        'badge': '소화효소제',
        'desc': '소화 효소 및 흡수 촉진에 뛰어난',
        # 기존 성분 (powerase_label_print.html 기준) - 파워라제는 소화효소제
        'ingredients': '바실러스 서브틸리스, 엔도 프로테아제, 알파 아밀라제, 라이페이스, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '소화',
        'eff1_sub': '효소 작용',
        'eff2': '흡수',
        'eff2_sub': '영양 흡수',
        'eff3': '회복',
        'eff3_sub': '수술 후',
        'eff4': '기력',
        'eff4_sub': '회복 촉진',
    },
    {
        'file': 'cancercare',
        'kor_name': '캔서케어',
        'eng_name': 'CANCERCARE',
        'color_primary': '6B7280',
        'color_secondary': '9CA3AF',
        'color_bg1': 'F9FAFB',
        'color_bg2': 'F3F4F6',
        'color_bg3': 'E5E7EB',
        'text_color': '111827',
        'sub_text': '374151',
        'accent_color': '4B5563',
        'icon_color1': 'F3F4F6',
        'icon_color2': 'E5E7EB',
        'icon_color3': 'D1D5DB',
        'icon_color4': '9CA3AF',
        'badge': '면역케어',
        'desc': '면역력 강화 및 항산화에 뛰어난',
        # 기존 성분 (cancercare_label_print.html 기준)
        'ingredients': '바실러스 서브틸리스, 베타글루칸, 알리신, 설포라판, 커큐민, 카테킨, AFNC, 정제수',
        'main_ing': '바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)',
        'eff1': '면역',
        'eff1_sub': '기능 강화',
        'eff2': '항산화',
        'eff2_sub': '세포 보호',
        'eff3': '활성',
        'eff3_sub': '산소 제거',
        'eff4': '체질',
        'eff4_sub': '개선 작용',
    },
]

for p in products:
    content = template
    
    # Title
    content = content.replace('MONSMECTA ORIGINAL — Premium Friendly (v2 개선판)', f'MONSMECTA {p["eng_name"]} — Premium Friendly')
    
    # Background colors
    content = content.replace('#F0F7F2', f'#{p["color_bg1"]}')
    content = content.replace('#E6F2EA', f'#{p["color_bg2"]}')
    content = content.replace('#FFF9F0', f'#{p["color_bg3"]}')
    
    # Primary colors
    content = content.replace('#4A7C59', f'#{p["color_primary"]}')
    content = content.replace('#3d6649', f'#{p["accent_color"]}')
    content = content.replace('#6BA583', f'#{p["color_secondary"]}')
    content = content.replace('#6B8A78', f'#{p["sub_text"]}')
    content = content.replace('#2F3E33', f'#{p["text_color"]}')
    content = content.replace('#5A6B60', f'#{p["sub_text"]}')
    content = content.replace('#F4C95D', f'#{p["color_secondary"]}')
    content = content.replace('#E8835A', f'#{p["color_primary"]}')
    content = content.replace('#C96A45', f'#{p["accent_color"]}')
    content = content.replace('#8A6A4A', f'#{p["sub_text"]}')
    content = content.replace('#7A6A58', f'#{p["sub_text"]}')
    content = content.replace('#E1EBE3', f'#{p["color_bg2"]}')
    content = content.replace('#F4E4BC', f'#{p["color_secondary"]}')
    content = content.replace('#FFF8E1', f'#{p["color_bg1"]}')
    
    # Product names
    content = content.replace('몬스멕타 <span class="text-[#4A7C59]">오리지널</span>', f'몬스멕타 <span class="text-[#{p["color_primary"]}]">{p["kor_name"]}</span>')
    content = content.replace('MONSMECTA ORIGINAL', f'MONSMECTA {p["eng_name"]}')
    content = content.replace('연변 · 설사에 강한 장 건강 솔루션', f'{p["desc"]} 솔루션')
    content = content.replace('배변케어', p['badge'])
    
    # Effect boxes - text
    content = content.replace('파보·로타·코로나 저항력', f'{p["eff1"]} {p["eff1_sub"]}')
    content = content.replace('건강 상태 유지', f'{p["eff2_sub"]}')
    content = content.replace('정장 작용 개선', f'{p["eff3"]} {p["eff3_sub"]}')
    content = content.replace('독소 제거·연변 개선', f'{p["eff4"]} {p["eff4_sub"]}')
    
    # Effect labels
    content = content.replace('>저항력<', f'>{p["eff1"]}<')
    content = content.replace('>면역<', f'>{p["eff2"]}<')
    content = content.replace('>장 기능<', f'>{p["eff3"]}<')
    content = content.replace('>해독<', f'>{p["eff4"]}<')
    
    # Icon background colors
    content = content.replace('bg-[#E8F5E9]', f'bg-[#{p["icon_color1"]}]')
    content = content.replace('bg-[#FFF8E1]', f'bg-[#{p["icon_color2"]}]')
    content = content.replace('bg-[#E3F2FD]', f'bg-[#{p["icon_color3"]}]')
    content = content.replace('bg-[#FCE4EC]', f'bg-[#{p["icon_color4"]}]')
    
    # 성분 박스는 기존 성분 그대로 사용 (5가지 복합체 대신 원료 명칭으로 변경)
    content = content.replace('핵심 5중 복합체', f'사용한 원료 ({p["badge"]})')
    
    # 기존 5가지 복합체 항목들을 실제 원료로 대체
    content = content.replace('Bacillus subtilis (고초균)', '바실러스 서브틸리스')
    content = content.replace('항균·항바이러스', '미생물제')
    content = content.replace('Glucose (포도당)', '포도당')
    content = content.replace('장 기능 개선·정장', '에너지 공급')
    content = content.replace('Vitamin A (비타민 A)', '비타민 A')
    content = content.replace('상피세포 회복', '상피세포 회복')
    content = content.replace('Sodium acetate / propionate', '아세트산나트륨 / 프로피온산나트륨')
    content = content.replace('전해질 보충', '전해질 보충')
    content = content.replace('Montmorillonite (몬모릴로나이트)', '몬모릴로나이트')
    content = content.replace('연변·설사 개선', '연변·설사 개선')
    
    # 우측 성분 정보 (원료 명칭 그대로)
    content = content.replace('바실러스 서브틸리스, 비타민A, 아세트산나트륨, 프로피온산나트륨, 포도당, 몬모릴로나이트, 정제수', p['ingredients'])
    content = content.replace('바실러스 서브틸리스 1.0 × 10⁷ CFU/g 이상, 부형제(정제수)', p['main_ing'])
    
    # Character colors
    content = content.replace('fill="#8B5A2B"', f'fill="#{p["color_primary"]}"')
    content = content.replace('fill="#D4A373"', f'fill="#{p["color_secondary"]}"')
    
    # Save
    output_path = rf'C:\Users\master\monsmecta_landing\public\assets\labels\{p["file"]}_label_print_v2_modern.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created: {p["file"]}_label_print_v2_modern.html')

print('\nAll 10 products generated with correct ingredients!')
