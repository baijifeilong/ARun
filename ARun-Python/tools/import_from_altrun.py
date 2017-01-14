with open('commands.txt', 'w') as file_to_write:
    with open('ShortCutList.txt') as f:
        for line in f:
            if line.strip():
                name = line[31:61].strip().replace(' ', '')
                path = line[line.rindex('|') + 1:].strip()
                print name
                print path
                file_to_write.write(name + '\t' + path + '\n')
