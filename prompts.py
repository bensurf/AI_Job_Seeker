scoring_prompt_phrases = [
    '''Below I will provide a letter of recommendation.''',

'''I would like you to extract the key words or phrases that commnunicate the overall "rating" of the applicant by the writer of the letter. Make sure that you only include words or phrases exactly as stated in the letter.
Any language indicating the candidate is top percentile or an outlier when compared to their peers is a good comment to include.

This rating is usually in the final paragraphs of the letter.

Make sure your response is in the following format:
--Key word or phrase 1
--Key words or phrase 2
--etc.''',

'''Here is the letter of recommendation:'''
]

scoring_prompt_rating = [
        '''Below I will provide a letter of recommendation.''',

'''I would like you to extract the applicants overall "rating" by the writer of the letter. This rating is usually in the final paragraphs of the letter.
Often this rating is in bold. In general, the tiers from high to low are:
--Exceptional
--Top x%
--Superb
--Outstanding
--Excellent
--Very high recommendation
--highest recommendation
--enthusiastic recommendation.

If the rating is not exactly one of those options, try to find the key word or phrase along those lines that sums up the overall rating.''',

'''In addition to the rating, please extract the full sentence in which you find the word or phrase.

Make sure your response is in the following JSON format:
{
"Rating" : "...",
"Full sentence" :,
}

Here is the letter of recommendation:'''
]

scoring_prompt_attributes = ['''Below I will provide a letter of recommendation.''',

'''Decide whether or not the listed attributes are mentioned in a positive manner in the letter of recommendation.
Only say YES if the attribute is specifically discussed in a highly positive manner, otherwise say NO.''',



'''Fill out the following JSON string by replacing <YES/NO> with either YES or NO. Do not elaborate or say anything besides the completed JSON. Here is the JSON:

{
        'Likeable' : <YES/NO>,
        'Work ethic' :  <YES/NO>,
        'Intelligent' :  <YES/NO>,
        'Clincial abilities' :  <YES/NO>,
        'Leader' :  <YES/NO>,
        'Team player' :  <YES/NO>,
        'Teacher' :  <YES/NO>,
        'Self-starter in research' : <YES/NO>,
}

Here is the letter of recommendation:

'''
]