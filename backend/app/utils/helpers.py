def combine_reviews(tripadvisor_reviews, google_reviews):
    combined_reviews = list(set(tripadvisor_reviews + google_reviews))
    return combined_reviews
