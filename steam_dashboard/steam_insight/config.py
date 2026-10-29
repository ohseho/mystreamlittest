"""Shared indicator definitions, fixed thresholds and report copy."""

MINT, BLUE, AMBER, MUTED = "#5DE4BE", "#80B8FF", "#F4BB72", "#9AABC2"

ALL_GENRES = "전체 장르"
REPORT_VIEW = "게임 리포트"
PATTERN_VIEW = "성공 패턴"

THRESHOLDS = {
    "reviews_7d": ("최근 7일 리뷰", 17, "개", "rate_review"),
    "ccu_retention": ("동접 유지율", 0.23, "%", "autorenew"),
    "followers_gain": ("팔로워 증가", 783, "명", "group_add"),
    "ccu_now": ("현재 동접", 27, "명", "sports_esports"),
    "twitch_peak": ("Twitch 최대 시청자", 2113, "명", "live_tv"),
}

FEATURE_DETAILS = {
    "reviews_7d": (
        "직전 7일간 새로 달린 리뷰 수입니다. 출시 30일 체크포인트 직전 7일에 추가된 "
        "긍정·부정 리뷰를 합친 값으로, 최근 이용자 반응을 살펴봅니다."
    ),
    "ccu_retention": (
        "현재 동접을 출시 후 그때까지의 최고 동접으로 나눈 비율입니다. 현재 동접은 직전 7일 평균을 뜻하며, "
        "초기 최고 동접 대비 최근 플레이어 규모가 얼마나 유지되는지 보여줍니다."
    ),
    "followers_gain": (
        "출시 후 늘어난 Steam 팔로워 수입니다. 출시 30일 시점의 팔로워 수에서 출시 시점의 기준 팔로워 수를 빼서, "
        "게임에 관심을 두는 이용자 규모의 변화를 확인합니다."
    ),
    "ccu_now": (
        "직전 7일 평균 동시접속자 수입니다. 이 데이터에서는 출시 30일 체크포인트 직전 7일의 "
        "일별 최고 동접을 평균해, 최근 플레이어 규모를 나타냅니다."
    ),
    "twitch_peak": (
        "출시일부터 30일 체크포인트까지 관측된 Twitch 시청자 수의 최댓값입니다. "
        "해당 기간에 게임 방송이 가장 많은 시청자를 모았을 때의 규모를 보여줍니다."
    ),
}

SIGNAL_SUMMARY_INSIGHTS = {
    frozenset(): (
        "지금은 이후의 리뷰 활동과 플레이어 규모를 함께 살펴보며, 초기 반응이 어떻게 달라지는지 지켜볼 시점입니다."
    ),
    frozenset({"reviews_7d"}): (
        "최근 리뷰 활동에서 반응이 확인되며, 플레이 규모와 팔로워·방송 관심에서도 반응이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"ccu_retention"}): (
        "출시 후 최고 동접 대비 이용 비율은 기준에 도달했으며, 최근 플레이어 규모와 새로운 관심이 함께 나타나는지 지켜볼 만합니다."
    ),
    frozenset({"followers_gain"}): (
        "팔로워 증가에서 관심의 확대가 확인되며, 리뷰와 플레이어 규모에도 비슷한 반응이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"ccu_now"}): (
        "최근 플레이어 규모는 기준에 도달했으며, 이 규모가 유지되고 리뷰와 관심의 확대로도 이어지는지 지켜볼 만합니다."
    ),
    frozenset({"twitch_peak"}): (
        "Twitch 최고 시청자 수에서 방송 관심이 확인됐으며, 이후 리뷰와 플레이 규모에서도 반응이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_retention"}): (
        "리뷰 활동과 피크 대비 동접 비율에서 반응이 나타났으며, 최근 플레이어 규모와 팔로워·방송 관심은 더 살펴볼 부분입니다."
    ),
    frozenset({"reviews_7d", "followers_gain"}): (
        "리뷰와 팔로워 증가에서 이용자 반응이 나타났으며, 최근 플레이어 규모와 동접 유지율에서도 강점이 나타나는지 지켜볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_now"}): (
        "최근 플레이어 규모와 리뷰 활동이 함께 기준에 도달했으며, 이용 규모의 유지와 팔로워·방송 관심의 확장을 지켜볼 만합니다."
    ),
    frozenset({"reviews_7d", "twitch_peak"}): (
        "리뷰 활동과 방송 최고 시청자 수에서 반응이 나타났으며, 플레이어 규모·유지율과 팔로워 증가도 함께 살펴볼 만합니다."
    ),
    frozenset({"ccu_retention", "followers_gain"}): (
        "피크 대비 동접 비율과 팔로워 증가가 기준에 도달했으며, 최근 플레이어 규모와 리뷰 활동에서도 반응이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"ccu_retention", "ccu_now"}): (
        "최근 플레이어 규모와 동접 유지율이 함께 기준에 도달해 플레이 지표에서 강점이 나타나며, 리뷰·팔로워·방송 반응은 더 지켜볼 부분입니다."
    ),
    frozenset({"ccu_retention", "twitch_peak"}): (
        "동접 유지율과 방송 최고 시청자 수가 기준에 도달했으며, 최근 플레이어 규모와 리뷰·팔로워 반응도 함께 살펴볼 만합니다."
    ),
    frozenset({"followers_gain", "ccu_now"}): (
        "팔로워 증가와 최근 플레이어 규모에서 반응이 나타났으며, 이 규모가 유지되고 리뷰 활동도 이어지는지 살펴볼 만합니다."
    ),
    frozenset({"followers_gain", "twitch_peak"}): (
        "팔로워 증가와 방송 최고 시청자 수에서 관심이 확인됐으며, 리뷰와 플레이어 규모·유지율에도 반응이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"ccu_now", "twitch_peak"}): (
        "최근 플레이어 규모와 방송 최고 시청자 수가 기준에 도달했으며, 동접 유지율과 리뷰·팔로워 반응도 함께 살펴볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_retention", "followers_gain"}): (
        "리뷰·팔로워 증가와 동접 유지율에서 고른 반응이 나타났으며, 최근 플레이어 규모와 방송 관심의 확대를 지켜볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_retention", "ccu_now"}): (
        "플레이어 규모와 유지율, 리뷰 활동이 함께 기준에 도달해 이용 측면의 강점이 보이며, 팔로워·방송 관심은 더 살펴볼 부분입니다."
    ),
    frozenset({"reviews_7d", "ccu_retention", "twitch_peak"}): (
        "리뷰 활동·동접 유지율·방송 최고 시청자 수에서 반응이 확인되며, 최근 플레이어 규모와 팔로워 증가도 함께 살펴볼 만합니다."
    ),
    frozenset({"reviews_7d", "followers_gain", "ccu_now"}): (
        "최근 플레이어 규모와 리뷰·팔로워 반응이 함께 나타났으며, 이용 규모의 유지와 방송 관심의 확장이 다음 관찰 지점입니다."
    ),
    frozenset({"reviews_7d", "followers_gain", "twitch_peak"}): (
        "리뷰·팔로워 증가·방송 최고 시청자 수에서 관심이 확인되며, 플레이어 규모와 동접 유지율에서도 반응이 나타나는지 지켜볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_now", "twitch_peak"}): (
        "플레이어 규모와 리뷰 활동, 방송 최고 시청자 수가 함께 기준에 도달했으며, 동접 유지율과 팔로워 증가를 더 살펴볼 만합니다."
    ),
    frozenset({"ccu_retention", "followers_gain", "ccu_now"}): (
        "플레이어 규모·유지율과 팔로워 증가에서 강점이 나타났으며, 리뷰 활동과 방송 관심에서도 반응이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"ccu_retention", "followers_gain", "twitch_peak"}): (
        "팔로워·방송 관심과 피크 대비 동접 비율이 기준에 도달했으며, 최근 플레이어 규모와 리뷰 활동도 함께 살펴볼 만합니다."
    ),
    frozenset({"ccu_retention", "ccu_now", "twitch_peak"}): (
        "플레이어 규모와 유지율, 방송 최고 시청자 수에서 반응이 확인되며, 리뷰와 팔로워 증가가 함께 나타나는지 지켜볼 만합니다."
    ),
    frozenset({"followers_gain", "ccu_now", "twitch_peak"}): (
        "플레이어 규모와 팔로워·방송 관심에서 반응이 나타났으며, 동접 유지율과 최근 리뷰 활동이 다음 관찰 지점입니다."
    ),
    frozenset({"ccu_retention", "followers_gain", "ccu_now", "twitch_peak"}): (
        "플레이 규모와 유지율, 팔로워·방송 관심이 고르게 나타났으며, 최근 리뷰 활동에서도 반응이 확인되는지 살펴볼 만합니다."
    ),
    frozenset({"reviews_7d", "followers_gain", "ccu_now", "twitch_peak"}): (
        "플레이어 규모와 리뷰·팔로워·방송 반응이 함께 나타났으며, 이 규모가 출시 후 최고 동접 대비 얼마나 유지되는지 더 살펴볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_retention", "ccu_now", "twitch_peak"}): (
        "플레이어 규모와 유지율, 리뷰·방송 반응이 함께 기준에 도달했으며, 팔로워 증가에서도 관심의 확대가 나타나는지 지켜볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_retention", "followers_gain", "twitch_peak"}): (
        "리뷰·팔로워·방송 관심과 동접 유지율이 기준에 도달했으며, 최근 플레이어 규모에서도 강점이 나타나는지 살펴볼 만합니다."
    ),
    frozenset({"reviews_7d", "ccu_retention", "followers_gain", "ccu_now"}): (
        "플레이어 규모와 유지율, 리뷰·팔로워 증가에서 고른 반응이 확인되며, 방송 관심의 확장도 함께 지켜볼 만합니다."
    ),
    frozenset(THRESHOLDS): (
        "리뷰·플레이 규모와 유지율·팔로워·방송 반응이 고르게 나타나, 이용과 관심이 함께 확인되는 긍정적인 출발입니다."
    ),
}

OUTCOMES = {1: "성공", 0: "미성공"}
