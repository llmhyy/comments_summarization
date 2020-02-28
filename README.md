To run decompose2.ipynb, first navigate to the local installation directory of Stanford CoreNLP,
then run this commmand:

```
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "tokenize,ssplit,pos,lemma,parse,sentiment" -port 9000 -timeout 30000
```
