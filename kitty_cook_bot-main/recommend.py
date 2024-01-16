import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from math import isnan
 
def recommend(survey):
    interactions_final = pd.read_csv("data/interactions_final.csv")
    recipes_include = pd.read_csv("data/recipes_include.csv")
 
    #print(interactions_final.groupby('user_id').count() >= 20)
 
    survey = pd.DataFrame(survey, columns=['user_id', 'recipe_id', 'rating'])
    survey = survey.drop(columns=['user_id'])
    survey['user_id'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    user_recipe_mark = survey[survey['rating'].notna()]
 
    inter_for_fit = interactions_final.append(user_recipe_mark, ignore_index=True)
 
    # оставляю только отмеченные рецепты
    users_for_calculation = inter_for_fit[inter_for_fit['recipe_id'].isin(user_recipe_mark['recipe_id'])]
    users_for_calculation = users_for_calculation.groupby(['user_id']).count()
    users_for_calculation.reset_index(inplace=True)
    # оставляю пользователей, которые отметили более 50% от числа оценок пользоваля
    users_for_calculation = users_for_calculation[users_for_calculation.recipe_id >= 0.5 * len(user_recipe_mark.index)]
 
    user_recipe_mat = inter_for_fit[(inter_for_fit['user_id'].isin(users_for_calculation['user_id'])) & (
        inter_for_fit['recipe_id'].isin(user_recipe_mark['recipe_id']))].sort_values(by=['user_id'],
                                                                                     ascending=[True]).pivot_table(
        index='user_id', columns='recipe_id', values='rating', aggfunc='mean')
    no_zeros = np.array(user_recipe_mat)
    no_zeros1 = np.nanmean(no_zeros, axis=1)
    for i in range(no_zeros.shape[0]):
        for j in range(no_zeros.shape[1]):
            if isnan(no_zeros[i][j]):
                no_zeros[i][j] = no_zeros1[i]
    user_recipe_mat_nozero = pd.DataFrame(data=no_zeros, columns=user_recipe_mat.columns, index=user_recipe_mat.index)
    user_recipe_mat_sparse = csr_matrix(user_recipe_mat_nozero.values)
    n = 20
    model_knn = NearestNeighbors(metric='cosine', algorithm='auto', n_neighbors=20, n_jobs=-1)
    model_knn.fit(user_recipe_mat_sparse)
    recom_index = 0
    distances, indices = model_knn.kneighbors(user_recipe_mat_sparse[recom_index], n_neighbors=20)
    distances_copy = distances.squeeze().tolist()[1:]
    indices_copy = indices.squeeze().tolist()[1:]
    import math
    for i in range(len(distances_copy)):
        distances_copy[i] = 1 - distances_copy[i]
    ids = list(user_recipe_mat_nozero.index)
    for i in range(len(indices_copy)):
        indices_copy[i] = ids[indices_copy[i]]
 
    # 1)исключить те рецепты, которые уже есть у пользователя,  2) добавить только похожих пользователей
    recipes_left = inter_for_fit[(~inter_for_fit['recipe_id'].isin(user_recipe_mark['recipe_id'])) & (
        inter_for_fit['user_id'].isin(indices_copy))]
    recs = recipes_left.groupby(['recipe_id']).count()
    recs.reset_index(inplace=True)
    recs = recs[recs.user_id >= 3]
 
    rec_users = pd.DataFrame(data=indices_copy, columns=['user_id'])
    rec_users['distance'] = distances_copy
 
    calc_mat = recipes_left[recipes_left['recipe_id'].isin(recs['recipe_id'])].pivot_table(index='user_id',
                                                                                           columns='recipe_id',
                                                                                           values='rating',
                                                                                           aggfunc='mean')
    marks = np.array(calc_mat)
 
    predict = []
 
    real_indices = list(calc_mat.index)
 
    for i in range(marks.shape[1]):
        predict.append([0, 0, 0, 0, 0])
        for j in range(marks.shape[0]):
            if not math.isnan(marks[j][i]):
                weight = dict(np.array(rec_users))[real_indices[j]]
                predict[i][int(marks[j][i]) - 1] += weight
 
    predict = []
 
    real_indices = list(calc_mat.index)
 
    for i in range(marks.shape[1]):
        predict.append([0, 0, 0, 0, 0])
        for j in range(marks.shape[0]):
            if not math.isnan(marks[j][i]):
                weight = dict(np.array(rec_users))[real_indices[j]]
                predict[i][int(marks[j][i]) - 1] += weight
 
    predict_norm = []
    for i in range(len(predict)):
        predict_norm.append([0, 0, 0, 0, 0])
        for j in range(5):
            predict_norm[i][j] = predict[i][j] / sum(predict[i])
 
    predicted_mark = []
    for i in range(len(predict_norm)):
        predicted_mark.append([0, 0])
        s = 0
        for j in range(5):
            s += (j + 1) * predict_norm[i][j]
        predicted_mark[i][0] = s
        predicted_mark[i][1] = sum(predict[i])
    test = pd.DataFrame(predicted_mark, columns=['predicted_mark', 'weight'])
    test['recipe_id'] = calc_mat.columns
 
    #test.sort_values(by=['predicted_mark', 'weight'], ascending=[False, False]).head(10)
    #res = test[(4.7 <= test['predicted_mark']) & (test['predicted_mark'] <= 5)].sort_values(by=['weight'],
     #                                                                                       ascending=[False])
    #for i in range(47, 10, -3):
    #    res = res.append(test[((i - 3) / 10 <= test['predicted_mark']) & (test['predicted_mark'] < i / 10)].sort_values(
   #         by=['weight'], ascending=[False]))
 
    #print(test.sort_values(by=['predicted_mark', 'weight'], ascending = [False, False]).head(20))
    # res.head(20).drop(columns = ['predicted_mark', 'weight'])
    res = test.sort_values(by=['predicted_mark', 'weight'], ascending=[False, False])
    print(res.head(10))
    temp_for_res = pd.merge(res.head(10).drop(columns=['predicted_mark', 'weight']),
                   recipes_include[['recipe_id', 'recipe_name', 'image_url']])
    retrn = []
    for i in list(temp_for_res.values):
        retrn.append(list(i))

    return retrn
 
if __name__ == '__main__':
    
    ss = recommend(survey = [(626264651, 6820, 1), (626264651, 8941, 5), (626264651, 10549, 5), (626264651, 12682, 5), (626264651, 15004, 4), (626264651, 16066, 1), (626264651, 23600, 1), (626264651, 26317, 3), (626264651, 50644, 5), (626264651, 56927, 5)])
    for i in ss:
        print(i)
