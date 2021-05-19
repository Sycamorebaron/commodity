import os
import pandas as pd

pd.set_option('expand_frame_repr', False)


hour_factor = {
    '09:00': 'nine',
    '09:30': 'nine_half',
    '10:00': 'ten',
    '10:30': 'ten_half',
    '11:00': 'eleven',
    '13:00': 'one',
    '13:30': 'one_half',
    '14:00': 'two',
}

for roots, dirs, files in os.walk(r'E:\commodity\data\output\hf_comm_factor'):
    if files:
        for f in files:
            print(f)
            data = pd.read_csv(os.path.join(roots, f))
            data['datetime'] = pd.to_datetime(data['datetime'])

            data = data[[i for i in data.columns if i not in hour_factor.keys()]]

            for seg in hour_factor.keys():
                data[hour_factor[seg]] = 0
                data.loc[data['datetime'].apply(lambda x: x.strftime('%H:%M') == seg), hour_factor[seg]] = 1
            data = data[data.columns[1:]].copy()

            data.to_csv(os.path.join(roots, f))
