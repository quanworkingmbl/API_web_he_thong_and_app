"""
Pre-LLM Rule Engine
Chạy trước khi gọi AI để:
- Reject ngay các trường hợp rõ ràng (tiết kiệm cost)
- Flag các trường hợp cần chú ý cho LLM
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RuleViolation:
    rule_name: str
    severity: str        # "reject" | "flag"
    description: str


@dataclass
class RuleResult:
    decision: str        # "PASS" | "REJECT" | "FLAG"
    violations: List[RuleViolation] = field(default_factory=list)

    @property
    def reasons(self) -> List[str]:
        return [v.description for v in self.violations]


# ==============================================================================
# PATTERNS & BLACKLISTS (Vietnamese context)
# ==============================================================================

# Số điện thoại Việt Nam (các đầu số phổ biến)
PHONE_PATTERNS = [
    re.compile(r'(?:0|\+84)\s*(?:\d[\s.-]*){9,10}', re.IGNORECASE),
    re.compile(r'(?:zalo|viber|telegram|whatsapp)\s*[:\-]?\s*[\d\s.+-]+', re.IGNORECASE),
]

# URL / Link ngoài sàn
URL_PATTERNS = [
    re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE),
    re.compile(r'www\.[^\s<>"\']+', re.IGNORECASE),
    re.compile(r'(?:shopee|lazada|tiki|sendo|facebook|fb)\.(?:vn|com)[^\s]*', re.IGNORECASE),
]

# Từ cấm — sản phẩm không được bán trên sàn đặc sản
# LƯU Ý: Dùng từ đầy đủ/cụ thể để tránh false positive
# Ví dụ: "kiếm" bị đổi thành "dao kiếm"/"gươm kiếm" vì "tìm kiếm" bị detect nhầm
BANNED_PRODUCT_KEYWORDS = [
    # Vũ khí, chất nổ
    "súng đạn", "súng lửa", "súng ống", "dao bấm", "dao kiếm", "gươm kiếm",
    "chất nổ", "thuốc nổ", "pháo nổ", "vũ khí",
    # Chất cấm
    "ma túy", "cần sa", "thuốc phiện", "heroin", "cocaine", "ecstasy", "ketamine",
    # Thuốc lá, rượu không phép
    "thuốc lá điện tử", "vape", "pod",
    # Hàng giả
    "hàng fake", "hàng nhái", "replica", "super fake",
    # Đồ dùng người lớn (không phù hợp sàn đặc sản)
    "đồ chơi người lớn", "sex toy",
    # Động vật hoang dã
    "ngà voi", "sừng tê", "vảy tê tê", "cao hổ", "mật gấu",
]

# Claim y tế không có chứng nhận
HEALTH_CLAIM_PATTERNS = [
    re.compile(r'chữa\s*(?:bệnh|ung\s*thư|tiểu\s*đường|cao\s*huyết\s*áp|viêm|đau)', re.IGNORECASE),
    re.compile(r'trị\s*(?:bệnh|ung\s*thư|tiểu\s*đường|liệu|dứt\s*điểm)', re.IGNORECASE),
    re.compile(r'phòng\s*(?:ngừa|chống)\s*(?:ung\s*thư|covid|bệnh)', re.IGNORECASE),
    re.compile(r'FDA\s*(?:approved|chứng\s*nhận|xác\s*nhận)', re.IGNORECASE),
    re.compile(r'(?:thuốc|dược\s*phẩm|thực\s*phẩm\s*chức\s*năng)\s+(?:chữa|trị|điều\s*trị)', re.IGNORECASE),
    re.compile(r'(?:cam\s*kết|đảm\s*bảo)\s+(?:khỏi|hết\s*bệnh|100%)', re.IGNORECASE),
]

# Nội dung phản cảm / tục tĩu
OFFENSIVE_PATTERNS = [
    re.compile(r'(?:đéo|đ[ịi]t|c[ặa]c|lồn|đ[ụu]\s*m[ẹe])', re.IGNORECASE),
]

# Nội dung nguy hiểm / bạo lực / kích động — REJECT ngay khi xuất hiện
# Rule này chạy trước LLM để bắt trường hợp AI bị "đánh lừa" bởi nội dung dài tích cực
VIOLENCE_KEYWORDS = [
    # Bạo lực thân thể
    "giết người", "giết chết", "sát hại", "thảm sát", "sát nhân",
    # Tự tử
    "tự tử", "tự vẫn", "tự sát",
    # Đe dọa trực tiếp
    "cho mày chết", "bị giết",
    # Kích động
    "khủng bố", "nổi loạn",
    # Bom, nổ (liên quan đến tấn công)
    "nổ tung", "phá hoại",
]

# Pattern bạo lực regex (bắt biến thể viết tắt, cách nhau khoảng trắng)
VIOLENCE_PATTERNS = [
    re.compile(r'gi\u1ebft\s*(?:ng\u01b0\u1eddi|ch\u1ebft|h\u1ea1i)', re.IGNORECASE),
    re.compile(r't\u1ef1\s*(?:t\u1eed|v\u1eaft|s\u00e1t)', re.IGNORECASE),
    re.compile(r's\u00e1t\s*(?:nh\u00e2n|h\u1ea1i)', re.IGNORECASE),
    re.compile(r'kh\u1ee7ng\s*b\u1ed1', re.IGNORECASE),
    re.compile(r'ch\u1ebft\s*(?:\u0111i|m\u1eb9|\u0111\u00e9o)', re.IGNORECASE),
]

# Danh mục cấm (category IDs — cần map với DB thực tế)
# Để rỗng vì phụ thuộc vào data seed, sẽ cấu hình sau
BANNED_CATEGORY_IDS: List[int] = []



# ==============================================================================
# RULE ENGINE
# ==============================================================================

class RuleEngine:
    """Pre-LLM rule engine để lọc nhanh trước khi gọi AI model."""

    @classmethod
    def check_product(
        cls,
        name: str,
        description: str = "",
        category_id: Optional[int] = None,
        price: float = 0,
        label: str = "",
    ) -> RuleResult:
        """
        Chạy tất cả rules cho sản phẩm.
        Return: RuleResult với decision PASS/REJECT/FLAG
        """
        violations: List[RuleViolation] = []
        combined_text = f"{name} {description}".lower()

        # 1. Check banned category
        if category_id and category_id in BANNED_CATEGORY_IDS:
            violations.append(RuleViolation(
                rule_name="banned_category",
                severity="reject",
                description=f"Danh mục sản phẩm bị cấm (category_id={category_id})"
            ))

        # 2. Check banned keywords — dùng word-boundary để tránh false positive
        # VD: "kiếm" không được match "tìm kiếm"
        for keyword in BANNED_PRODUCT_KEYWORDS:
            # \b không hoạt động tốt với Unicode Vietnamese → dùng lookaround space/start/end
            pattern = r'(?<![\wàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ])' + re.escape(keyword.lower()) + r'(?![\wàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ])'
            if re.search(pattern, combined_text):
                violations.append(RuleViolation(
                    rule_name="banned_keyword",
                    severity="reject",
                    description=f"Chứa từ khóa cấm: '{keyword}'"
                ))
                break  # Một từ cấm đủ để reject

        # 3. Check phone numbers
        for pattern in PHONE_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="phone_number",
                    severity="reject",
                    description="Chứa số điện thoại/liên hệ trong mô tả"
                ))
                break

        # 4. Check external URLs
        for pattern in URL_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="external_url",
                    severity="reject",
                    description="Chứa đường link/URL bên ngoài sàn"
                ))
                break

        # 5. Check health claims
        for pattern in HEALTH_CLAIM_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="health_claim",
                    severity="flag",
                    description="Có thể chứa claim y tế chưa được xác minh"
                ))
                break

        # 6. Check offensive content
        for pattern in OFFENSIVE_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="offensive_content",
                    severity="reject",
                    description="Chứa nội dung phản cảm"
                ))
                break

        # 7. Check VIOLENCE / dangerous content — ưu tiên cao nhất
        for keyword in VIOLENCE_KEYWORDS:
            if keyword in combined_text:
                violations.append(RuleViolation(
                    rule_name="violence_content",
                    severity="reject",
                    description=f"Chứa nội dung bạo lực / nguy hiểm: '{keyword}'"
                ))
                break
        else:
            for pattern in VIOLENCE_PATTERNS:
                if pattern.search(combined_text):
                    violations.append(RuleViolation(
                        rule_name="violence_content",
                        severity="reject",
                        description="Chứa ngôn từ bạo lực / kích động nguy hiểm"
                    ))
                    break

        # 8. Price anomaly (flag only)
        if price > 0:
            if price < 500:
                violations.append(RuleViolation(
                    rule_name="price_anomaly",
                    severity="flag",
                    description=f"Giá quá thấp: {price} VND"
                ))
            elif price > 50_000_000:
                violations.append(RuleViolation(
                    rule_name="price_anomaly",
                    severity="flag",
                    description=f"Giá rất cao: {price:,.0f} VND — cần xem lại"
                ))

        # Determine decision
        has_reject = any(v.severity == "reject" for v in violations)
        has_flag = any(v.severity == "flag" for v in violations)

        if has_reject:
            decision = "REJECT"
        elif has_flag:
            decision = "FLAG"
        else:
            decision = "PASS"

        result = RuleResult(decision=decision, violations=violations)

        logger.info(
            "RuleEngine: decision=%s violations=%d [%s]",
            decision, len(violations),
            ", ".join(v.rule_name for v in violations) or "none"
        )

        return result

    @classmethod
    def check_content(
        cls,
        title: str,
        content_text: str = "",
        content_type: str = "",
    ) -> RuleResult:
        """Chạy rules cho content/blog. Tương tự product nhưng bỏ price check."""
        violations: List[RuleViolation] = []
        combined_text = f"{title} {content_text}".lower()

        # Check banned keywords — word-boundary match
        for keyword in BANNED_PRODUCT_KEYWORDS:
            pattern = r'(?<![\wàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ])' + re.escape(keyword.lower()) + r'(?![\wàáâãèéêìíòóôõùúýăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ])'
            if re.search(pattern, combined_text):
                violations.append(RuleViolation(
                    rule_name="banned_keyword",
                    severity="reject",
                    description=f"Chứa từ khóa cấm: '{keyword}'"
                ))
                break

        # Check phone numbers
        for pattern in PHONE_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="phone_number",
                    severity="flag",
                    description="Chứa số điện thoại trong nội dung"
                ))
                break

        # Check external URLs
        for pattern in URL_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="external_url",
                    severity="flag",
                    description="Chứa đường link bên ngoài"
                ))
                break

        # Check health claims
        for pattern in HEALTH_CLAIM_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="health_claim",
                    severity="flag",
                    description="Có thể chứa claim y tế chưa xác minh"
                ))
                break

        # Check offensive
        for pattern in OFFENSIVE_PATTERNS:
            if pattern.search(combined_text):
                violations.append(RuleViolation(
                    rule_name="offensive_content",
                    severity="reject",
                    description="Chứa nội dung phản cảm"
                ))
                break

        # Check VIOLENCE / dangerous content — quan trọng nhất!
        for keyword in VIOLENCE_KEYWORDS:
            if keyword in combined_text:
                violations.append(RuleViolation(
                    rule_name="violence_content",
                    severity="reject",
                    description=f"Chứa nội dung bạo lực / nguy hiểm: '{keyword}'"
                ))
                break
        else:
            for pattern in VIOLENCE_PATTERNS:
                if pattern.search(combined_text):
                    violations.append(RuleViolation(
                        rule_name="violence_content",
                        severity="reject",
                        description="Chứa ngôn từ bạo lực / kích động nguy hiểm"
                    ))
                    break

        has_reject = any(v.severity == "reject" for v in violations)
        has_flag = any(v.severity == "flag" for v in violations)

        if has_reject:
            decision = "REJECT"
        elif has_flag:
            decision = "FLAG"
        else:
            decision = "PASS"

        return RuleResult(decision=decision, violations=violations)
