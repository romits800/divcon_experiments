
def levenshtein_distance(s, t):
        d = [[0 for i in range(len(s)+1)] for j in range(len(t)+1)]
        for i in range(1, len(s)+1):
                d[0][i] = i
        for i in range(1, len(t)+1):
                d[i][0] = i

        for i in range(1, len(s)+1):
                for j in range(1, len(t)+1):
                        subcost = 0 if s[i-1] == t[j-1] else 1
                        d[j][i] = min( d[j-1][i] + 1, d[j][i-1] +1 , d[j-1][i-1] + subcost)

        return d[-1][-1]

def levenshtein_sets(s, t):
        d = [[0 for i in range(len(s)+1)] for j in range(len(t)+1)]
        for i in range(1, len(s)+1):
                d[0][i] = d[0][i-1] + len(s[i-1])
        for i in range(1, len(t)+1):
                d[i][0] = d[i-1][0] + len(t[i-1])

        print d
        for i in range(1, len(s)+1):
                for j in range(1, len(t)+1):
                    card = max(len(s[i-1]-t[j-1]), len(t[j-1]-s[i-1]))
                    subcost = card #0 if s[i-1] == t[j-1] else card
                    v1 = d[j-1][i] + len(t[j-1])
                    v2 = d[j][i-1] + len(s[i-1])
                    d[j][i] = min( v1, v2, d[j-1][i-1] + subcost)

        print d
        return d[-1][-1]
