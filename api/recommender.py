def generate_retention_recommendations(top_features):

    recommendations = []

    mapping = {
        "Contract_Month-to-month":
            "Offer discounted annual contract upgrade",

        "tenure":
            "Launch customer loyalty campaign",

        "MonthlyCharges":
            "Provide personalized pricing offer",

        "InternetService_Fiber optic":
            "Offer premium support package",

        "OnlineSecurity_No":
            "Bundle cybersecurity add-on",

        "TechSupport_No":
            "Provide free onboarding support"
    }

    for feature in top_features:
        if feature in mapping:
            recommendations.append(mapping[feature])

    if len(recommendations) == 0:
        recommendations.append(
            "Assign retention specialist for review"
        )

    return recommendations[:3]