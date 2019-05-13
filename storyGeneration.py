import tree_parsing
import json
def main():
    #frange = ['1', '2', '11', '12', '13', '14', '15']
    frange=['12']
    for fno in frange:
        fname = "stories/story" + fno
        print("storyyyy", fname)
        data_received = tree_parsing.parsing(fname)
        with open('StoryGrammer' + fno + '.json', 'w') as outfile:
            json.dump(data_received, outfile)

        fh = open('readableSg' + fno + '.txt', 'w')
        for key, val in data_received.items():
            fh.write(str(val))
            fh.write('\n\n')
        fh.close()

        print("DONE")


main()