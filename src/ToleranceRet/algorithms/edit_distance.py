def Edit_distance(s1, s2):
    rows = len(s1) + 1
    cols = len(s2) + 1

    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        matrix[i][0] = i
    for j in range(cols):
        matrix[0][j] = j

    for i in range(1, rows):
        for j in range(1, cols):

            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1

            matrix[i][j] = min(
                matrix[i - 1][j] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j - 1] + cost
            )

    return matrix[-1][-1]

if __name__ == "__main__":
    word1 = "protein"
    word2 = "protien"

    distance = Edit_distance(word1, word2)
    print(f"The edit distance between '{word1}' and '{word2}' is: {distance}")