# Monitoring the youtube-trends

In this repository I collect data about the German YouTube trends. My main goal is to understand the algorithm behind the trending page.
At the moment I collect the trending data every 6 hours. Notably the data includes not just the pure trends data,
but also the basic stats about the last 50 videos uploaded by the trending videos uploader, since I suspect, an above average video performance
is the deciding factor for entering the trends. The collected data may expand in the future.

### Future Additions
- In the future I would like to include data about videos which could possibly trend, if I find patterns which allow me some means of prediction.
- Also I will add combined stats over several data collections which include changes in trending rank, time the video was trending and similar stats.

### Scope
Since the youtube-api allows 10.000 api requests at base level just the German YouTube trends are monitored.

### Current State
I missed a python change wich broke my api-client. Therefore this repo will not get any new updates.
If i have the leisure to redo the client, the new repo will be linked here.
