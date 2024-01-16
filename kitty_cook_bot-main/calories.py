def calories_possible(sex, height, age, weight_current, intensity, deficiency): 
    if sex == 'F':    
        return int((655.1 + (9.563 * weight_current) 
            + (1.85 * height) - (4.676 * age)) * intensity * ((100 - deficiency) / 100)) 
    else:
        return int((66.5 + (13.75 * weight_current) 
            + (5.003 * height) - (6.775 * age)) * intensity * ((100 - deficiency) / 100))
