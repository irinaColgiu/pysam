pysam
=====

Slightly modified version of pysam 0.7.1 -- it contains 2 small changes:

1. I've included "DS" tag in the "PG" entry of the header:

<pre>
VALID_HEADER_FIELDS = { "HD" : { "VN" : str, "SO" : str, "GO" : str },
                        "SQ" : { "SN" : str, "LN" : int, "AS" : str, "M5" : str, "UR" : str, "SP" : str },
                        "RG" : { "ID" : str, "SM" : str, "LB" : str, "DS" : str, "PU" : str, "PI" : str, 
                                 "CN" : str, "DT" : str, "PL" : str, "FO" : str, "KS" : str, "PG" : str,},
                        "PG" : { "PN" : str, "ID" : str, "VN" : str, "CL" : str, "PP" : str, **"DS" : str** }, }

#output order of fields within records:

VALID_HEADER_ORDER = { "HD" : ( "VN", "SO", "GO" ),
                       "SQ" : ( "SN", "LN", "AS", "M5" , "UR" , "SP" ),
                       "RG" : ( "ID", "SM", "LB", "DS" , "PU" , "PI" , "CN" , "DT", "PL", "FO", "KS", "PG" ),
                       "PG" : ( "PN", "ID", "VN", "CL", "PP", **"DS"** ), }
</pre>
                       
2. I have replaced within VALID_HEADER_ORDER the tuples with sets - so that the order won't matter any more:
 
<pre>
VALID_HEADER_ORDER = { "HD" : ( "VN", "SO", "GO" ),
                       "SQ" : ( "SN", "LN", "AS", "M5" , "UR" , "SP" ),
                       "RG" : ( "ID", "SM", "LB", "DS" , "PU" , "PI" , "CN" , "DT", "PL", "FO", "KS", "PG" ),
                       "PG" : ( "PN", "ID", "VN", "CL", "PP", "DS" ), }
</pre>
===> 
<pre>
VALID_HEADER_ORDER = { "HD" : { "VN", "SO", "GO" },
                       "SQ" : { "SN", "LN", "AS", "M5" , "UR" , "SP" },
                       "RG" : { "ID", "SM", "LB", "DS" , "PU" , "PI" , "CN" , "DT", "PL", "FO", "KS", "PG" },
                       "PG" : { "PN", "ID", "VN", "CL", "PP", "DS" }, }
</pre>

That's all.
