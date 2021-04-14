from numpy import number


def read_in_train_file(how_many_rows=0):
    path = './data_set/train.csv'
    data = []
    
    with open(path, 'r') as in_file:
        for i, line in enumerate(in_file):
            line = line.strip('\n')
            line = line.split(',')
            del line[1]
            del line[5]
            
            if i == 0:
                line[6] = 'question_elapsed_time'
                line[7] = 'question_had_explanation'
                line.append('question_counter')
                line.append('time_group')
                # Original
                # row_id,timestamp,user_id,content_id,content_type_id,task_container_id,
                # user_answer,answered_correctly,prior_question_elapsed_time,prior_question_had_explanation

                """
                Removing timestamp and user_answer. Doesn't matter how long time the person spent without answering the question since some ppl
                take a break or something between sittings and also what their answer are.
                """
            elif i != how_many_rows+1:
                line.append('0')
                line.append('0')
                for i, element in enumerate(line):
                    if element == '':
                        line[i] = '0'
            else:
                break
            data.append(line)                  
     
    return data

def save_file(file_name, data):
    path = './data_set/new/'

    new_data = []
    for row in data:
        row = (',').join(row)
        new_data.append(row)

    with open(path + file_name, 'w') as out_file:
        for row in new_data:
            out_file.write(str(row) + '\n')

def create_new_data(raw_data):
    """
        0:row_id,
        1:user_id,
        2:content_id,
        3:content_type_id,
        4:task_container_id,
        5:answered_correctly,
        6:question_elapsed_time,
        7:question_had_explanation,
        8:counter_question,
        9:content_id_content
    """
    def step1(raw_data):
        data = raw_data
        extra_data = data.copy()
        step1_data = []
        
        counter = 0
        number_rows = len(extra_data)-1

        for i, line in enumerate(data): #Moves question time to one row before. So can remove prior from that.
            user_now = line[1]
        
            if i != 0:
                counter += 1
                line[8] = str(counter)

            if i < number_rows and i > 0:
                user_next = extra_data[i+1][1]
                line[6] = str(int(round((int(float(extra_data[i+1][6])) / 1000), 0))) #Converts time from ms to seconds
                line[7] = extra_data[i+1][7] # Takes explanation from row before 
            else:
                user_next = line[1]

            if user_now != user_next:
                line[6] = extra_data[i-1][6]
                line[7] = extra_data[i-1][7]
                counter=0
            
            if line[5] == '-1': #answered_correctly: (int8) if the user responded correctly. Read -1 as null, for lectures.
                line[5] = '0' #Sets 0 for easier to use with pandas... but should be null

            if line[7] == '0':
                line[7] = 'False'
            
            
            
            if i == number_rows:
                line[6] = str(int(round((int(float(extra_data[i][6])) / 1000), 0)))
                
            if i != 0:
                time_group = int(line[6])
                # print(f'1. time_group: {time_group}, line[9]: {line[9]}, line: {line}')
                if time_group < 10:
                    line[9] = '1'
                elif time_group < 20:
                    line[9] = '2'
                elif time_group < 30:
                    line[9] = '3'
                elif time_group < 40:
                    line[9] = '4'
                elif time_group < 50:
                    line[9] = '5'
                elif time_group < 60:
                    line[9] = '6'
                elif time_group < 70:
                    line[9] = '7'
                elif time_group < 80:
                    line[9] = '8'
                elif time_group < 90:
                    line[9] = '9'
                elif time_group < 100:
                    line[9] = '10'
                else:
                    line[9] = '11'

            step1_data.append(line)



        return step1_data

    def add_content_id_content(old_data):
        def read_in_questions():
            question_data = []
            with open('./data_set/questions.csv', 'r') as in_file:
                for line in in_file:
                    line = line.strip()
                    line = line.split(',')
                    question_data.append(line)
            return question_data

        def read_in_lectures():
            lectures_data = []
            tags_in_lectures = []
            with open('./data_set/lectures.csv', 'r') as in_file:
                for i, line in enumerate(in_file):
                    line = line.strip()
                    line = line.split(',')
                    if line[1] not in tags_in_lectures and i != 0:
                        tags_in_lectures.append(line[1])
                    lectures_data.append(line)
            tags_in_lectures.sort(key=int)

            return lectures_data, tags_in_lectures

        def remove_unnecessary_tags_in_questions(data_question, tag_list_lectures):
            new_data = []
            for i, line in enumerate(data_question):
                if i != 0:
                    line[4] = line[4].split(" ")
                    tags = line[4]
                    for j, tag in enumerate(tags):
                        if tag not in tag_list_lectures:
                            line[4][j] = ''
                    line[4] = (' ').join(line[4])
                    line[4] = line[4].strip()
                    
                new_data.append(line)
            return new_data

        questions_raw_data = read_in_questions()
        lectures_raw_data, tags_in_lectures = read_in_lectures()
        questions_cleaned_data = remove_unnecessary_tags_in_questions(questions_raw_data, tags_in_lectures)

        def get_question_or_lecture(target_content_id, content_type_id):
            question_data = questions_cleaned_data.copy()
            lectures_data = lectures_raw_data.copy()
            if content_type_id == '0':
                for line in question_data:
                    if line[0] == target_content_id:
                        line = (' ').join(line)
                        return line
            else:
                for line in lectures_data:
                    if line[0] == target_content_id:
                        line = (' ').join(line)
                        return line
            
        new_data = []
        for i, line in enumerate(old_data):
            if i != 0:
                content_id = line[2]
                content_type_id = line[3]
                line[9] = get_question_or_lecture(content_id, content_type_id)
            new_data.append(line)
        return new_data

    step1_data = step1(raw_data)
    #step2_data = add_content_id_content(step1_data)
    step2_data = step1_data
    return step2_data

def main():
    raw_data = read_in_train_file(5000000)
    
    new_data = create_new_data(raw_data)


    save_file('train_five_million.csv', new_data)


if __name__ == '__main__':
    main()
