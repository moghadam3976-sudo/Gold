# utils/geological_analysis.py
# -*- coding: utf-8 -*-
import json
from typing import Dict, List, Tuple

class GeologicalAnalyzer:
    """تجزیه‌کننده جیولوژیکی متخصص"""
    
    def __init__(self):
        self.indicators_weights = {
            "color": 15,
            "hardness": 15,
            "luster": 10,
            "crystal_structure": 12,
            "streak": 10,
            "magnetism": 8,
            "specific_gravity": 15,
            "cleavage": 10,
            "oxidation": 5
        }
        
        self.geological_data = self.load_geological_data()
    
    def load_geological_data(self) -> Dict:
        """بارگذاری داده‌های جیولوژیکی"""
        return {
            "gold_indicators": {
                "colors": ["زرد درخشان", "نارنجی متالیک", "سفید مایل"],
                "hardness_range": [2.5, 3.0],
                "gravity_range": [19.0, 19.5],
                "association": ["کوارتز سفید", "پیریت", "پوتاسیم فلدسپار"]
            },
            "gemstone_indicators": {
                "colors": ["قرمز", "آبی", "سبز", "صورتی", "بنفش"],
                "hardness_range": [7.0, 10.0],
                "luster": ["درخشان", "شیشه‌ای", "الماسی"],
                "crystal_forms": ["بلور شش‌گوش", "بلور مثلث‌شکل", "بلور مکعبی"]
            },
            "provinces": {
                "خراسان رضوی": {"gold_probability": 0.75, "gemstone_probability": 0.45},
                "کرمانشاه": {"gold_probability": 0.80, "gemstone_probability": 0.35},
                "اصفهان": {"gold_probability": 0.70, "gemstone_probability": 0.65},
                "کرمان": {"gold_probability": 0.85, "gemstone_probability": 0.75},
                "هرمزگان": {"gold_probability": 0.55, "gemstone_probability": 0.80},
                "قم": {"gold_probability": 0.45, "gemstone_probability": 0.50},
                "چهارمحال و بختیاری": {"gold_probability": 0.65, "gemstone_probability": 0.55},
                "خوزستان": {"gold_probability": 0.60, "gemstone_probability": 0.40},
                "لرستان": {"gold_probability": 0.70, "gemstone_probability": 0.45},
                "سمنان": {"gold_probability": 0.65, "gemstone_probability": 0.60},
            }
        }
    
    def calculate_indicators(self, answers: Dict) -> Dict:
        """محاسبه شاخص‌های جیولوژیکی"""
        indicators = {}
        total_weight = 0
        total_score = 0
        
        for indicator, weight in self.indicators_weights.items():
            if indicator in answers:
                score = answers[indicator] * weight
                indicators[indicator] = score
                total_weight += weight
                total_score += score
        
        # نرمال‌سازی امتیاز (0-100)
        normalized_score = (total_score / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "detailed_indicators": indicators,
            "total_score": normalized_score,
            "weights": self.indicators_weights
        }
    
    def generate_geological_report(self, answers: Dict, province: str = None) -> Dict:
        """تولید گزارش جیولوژیکی جامع"""
        
        indicators_result = self.calculate_indicators(answers)
        score = indicators_result["total_score"]
        
        # تحلیل احتمالات
        gold_probability = self.analyze_gold_probability(answers, province)
        gemstone_probability = self.analyze_gemstone_probability(answers, province)
        
        # تحلیل ساختار و فرم
        structure_analysis = self.analyze_structure(answers)
        
        # پیشنهادات عملی
        recommendations = self.generate_recommendations(answers, score)
        
        return {
            "score": score,
            "gold_probability": gold_probability,
            "gemstone_probability": gemstone_probability,
            "structure_analysis": structure_analysis,
            "recommendations": recommendations,
            "indicators": indicators_result,
            "next_steps": self.generate_next_steps(score, gold_probability, gemstone_probability)
        }
    
    def analyze_gold_probability(self, answers: Dict, province: str = None) -> float:
        """تجزیه احتمال طلا"""
        base_probability = 0.5
        
        # تأثیر رنگ
        if answers.get("color_score", 0) > 70:
            base_probability += 0.20
        
        # تأثیر ارتباط کانی‌ای
        if answers.get("quartz_association", 0) == 1:
            base_probability += 0.15
        
        # تأثیر وزن مخصوص
        if answers.get("gravity_score", 0) > 60:
            base_probability += 0.15
        
        # تأثیر منطقه جغرافیایی
        if province and province in self.geological_data["provinces"]:
            base_probability += self.geological_data["provinces"][province]["gold_probability"] * 0.10
        
        return min(base_probability, 1.0)
    
    def analyze_gemstone_probability(self, answers: Dict, province: str = None) -> float:
        """تجزیه احتمال جواهر"""
        base_probability = 0.3
        
        # تأثیر رنگ
        if answers.get("color_vibrance", 0) > 75:
            base_probability += 0.20
        
        # تأثیر سختی
        if answers.get("hardness_score", 0) > 70:
            base_probability += 0.15
        
        # تأثیر تابش
        if answers.get("luster_score", 0) > 75:
            base_probability += 0.15
        
        # تأثیر منطقه جغرافیایی
        if province and province in self.geological_data["provinces"]:
            base_probability += self.geological_data["provinces"][province]["gemstone_probability"] * 0.10
        
        return min(base_probability, 1.0)
    
    def analyze_structure(self, answers: Dict) -> Dict:
        """تجزیه ساختار بلوری"""
        return {
            "crystal_form": self.determine_crystal_form(answers),
            "cleavage_pattern": self.analyze_cleavage(answers),
            "oxidation_state": self.analyze_oxidation(answers),
            "fracture_type": self.determine_fracture_type(answers)
        }
    
    def determine_crystal_form(self, answers: Dict) -> str:
        """تعیین فرم بلوری"""
        crystal_score = answers.get("crystal_structure", 0)
        
        if crystal_score > 80:
            return "بلور کامل و منظم (احتمال بالای معدن قیمتی)"
        elif crystal_score > 60:
            return "بلور نیمه‌تشکیل شده (ممکن است پتانسیل طلا)"
        elif crystal_score > 40:
            return "بلور ناقص (نیاز به بررسی بیشتر)"
        else:
            return "بدون ساختار بلوری واضح"
    
    def analyze_cleavage(self, answers: Dict) -> str:
        """تجزیه شکاف‌خوری"""
        cleavage_score = answers.get("cleavage", 0)
        
        if cleavage_score > 70:
            return "شکاف‌خوری واضح - نشانه‌ی ساختار بلوری قوی"
        elif cleavage_score > 40:
            return "شکاف‌خوری ضعیف - احتمال معادن ثانویه"
        else:
            return "بدون شکاف‌خوری - احتمال معادن شن‌وماسه‌ای"
    
    def analyze_oxidation(self, answers: Dict) -> str:
        """تجزیه میزان اکسیداسیون"""
        oxidation_score = answers.get("oxidation", 0)
        
        if oxidation_score > 70:
            return "اکسیداسیون بالا - احتمال سن زیاد معدن"
        elif oxidation_score > 40:
            return "اکسیداسیون متوسط - احتمال معدن میانسال"
        else:
            return "اکسیداسیون کم - احتمال معدن نسبتاً تازه"
    
    def determine_fracture_type(self, answers: Dict) -> str:
        """تعیین نوع شکست"""
        fracture_score = answers.get("hardness", 0)
        
        if fracture_score > 75:
            return "شکست خواردگی (معمول در سنگ‌های سخت)"
        elif fracture_score > 50:
            return "شکست نیمه‌شاخ (معدن متوسط"
        else:
            return "شکست ناهموار (معدن نرم)"
    
    def generate_recommendations(self, answers: Dict, score: float) -> List[str]:
        """تولید پیشنهادات عملی"""
        recommendations = []
        
        if score > 75:
            recommendations.append("🔨 استفاده از تجهیزات معدن‌کاری حرفه‌ای توصیه می‌شود")
            recommendations.append("🧪 انجام آزمایش‌های شیمیایی تخصصی ضروری است")
            recommendations.append("📍 ثبت موقعیت دقیق برای بررسی‌های بعدی")
        elif score > 50:
            recommendations.append("🔍 بررسی مجدد با دقت بیشتر نیاز است")
            recommendations.append("📊 جمع‌آوری نمونه‌های بیشتر برای تحلیل مقایسه‌ای")
            recommendations.append("💎 مشاوره با متخصص جیولوژی بومی منطقه")
        else:
            recommendations.append("⚠️ ممکن است این معدن ارزش بررسی دقیق نداشته باشد")
            recommendations.append("🔎 جستجو در مناطق دیگر پیشنهاد می‌شود")
        
        return recommendations
    
    def generate_next_steps(self, score: float, gold_prob: float, gem_prob: float) -> List[str]:
        """تولید مراحل بعدی"""
        steps = []
        
        if max(gold_prob, gem_prob) > 0.7:
            steps.append("1️⃣ استخراج نمونه احتیاط‌شده برای آزمایشگاه")
            steps.append("2️⃣ ارسال به آزمایشگاه معادن رسمی")
            steps.append("3️⃣ دریافت گواهی رسمی از معدن")
            steps.append("4️⃣ مشاوره با متخصصان استخراج")
        elif max(gold_prob, gem_prob) > 0.5:
            steps.append("1️⃣ جمع‌آوری نمونه‌های بیشتر")
            steps.append("2️⃣ بررسی میدانی تخصصی‌تر")
            steps.append("3️⃣ مقایسه با نمونه‌های معیار")
        
        return steps
