#bash
echo '' > validation-report.txt

myFiles=`find /home/thanasis/Documents/research-work/projects/2019-linked-conservation-data/repositories/board-pilot-data -name "*.rdf"`

for myFile in $myFiles
do
echo "$myFile" >> validation-report.txt
response="$(rapper -c -g $myFile 2>&1)"
echo $response >> validation-report.txt
done
