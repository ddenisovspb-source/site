import pandas as pd
import re
import os

class OlapCube:
    def __init__(self, excel_path=None):
        if excel_path is None:
            excel_path = 'data/olap_fixed.xlsx'
        
        self.excel_path = excel_path
        self.projects = []
        self.all_data = None
        self.column_names = []
        self.load_data()
    
    def load_data(self):
        if not os.path.exists(self.excel_path):
            print(f"❌ Файл не найден: {self.excel_path}")
            return
        
        df_raw = pd.read_excel(self.excel_path, header=None, engine='openpyxl')
        
        for idx, row in df_raw.iterrows():
            if pd.notna(row[1]) and 'Месяц' in str(row[1]):
                self.column_names = []
                for col in row:
                    if pd.notna(col):
                        self.column_names.append(str(col).strip())
                    else:
                        break
                break
        
        current_project = None
        for idx, row in df_raw.iterrows():
            if pd.notna(row[0]) and isinstance(row[0], str):
                if idx + 1 < len(df_raw):
                    next_row = df_raw.iloc[idx + 1]
                    if pd.notna(next_row[1]) and 'Месяц' in str(next_row[1]):
                        current_project = {
                            'name': row[0].strip(),
                            'header_row': idx + 1,
                            'data_start': idx + 2,
                            'data_end': None
                        }
                        continue
            
            if current_project and current_project['data_end'] is None:
                if pd.isna(row[1]) and pd.isna(row[0]):
                    current_project['data_end'] = idx
                    self.projects.append(current_project)
                    current_project = None
                elif 'Итого' in str(row[0]):
                    current_project['data_end'] = idx + 1
                    self.projects.append(current_project)
                    current_project = None
        
        all_rows = []
        for project in self.projects:
            for row_idx in range(project['data_start'], project['data_end']):
                if row_idx >= len(df_raw):
                    break
                row_data = df_raw.iloc[row_idx]
                
                if pd.isna(row_data[1]) and pd.isna(row_data[0]):
                    continue
                if 'Итого' in str(row_data[0]):
                    continue
                
                row_dict = {'Проект': project['name']}
                for i, col_name in enumerate(self.column_names):
                    if i < len(row_data):
                        val = row_data[i]
                        if isinstance(val, (int, float)):
                            row_dict[col_name] = val
                        else:
                            row_dict[col_name] = val if pd.notna(val) else None
                
                all_rows.append(row_dict)
        
        self.all_data = pd.DataFrame(all_rows)
        self.all_data.columns = [col.replace(':', '').strip() for col in self.all_data.columns]
        
        if 'Месяц' in self.all_data.columns:
            self.all_data['Месяц'] = pd.to_datetime(self.all_data['Месяц'])
        
        print(f"✅ Загружено {len(self.all_data)} строк")
        print(f"📋 Проекты: {[p['name'] for p in self.projects]}")
    
    def get_projects(self):
        return [p['name'] for p in self.projects]
    
    def get_columns(self):
        return list(self.all_data.columns)
    
    def query(self, projects=None, columns=None):
        df = self.all_data.copy()
        
        if projects and len(projects) > 0:
            df = df[df['Проект'].isin(projects)]
        
        if columns and len(columns) > 0:
            available_cols = [col for col in columns if col in df.columns]
            if 'Проект' not in available_cols:
                available_cols = ['Проект'] + available_cols
            df = df[available_cols]
        
        if 'Месяц' in df.columns:
            df = df.sort_values(['Проект', 'Месяц'])
            df['Месяц'] = df['Месяц'].dt.strftime('%Y-%m-%d')
        
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')
