# Copyright (C) 2023 David Joffe / DJ Software
# Simple regex replace that does not actually need AI (if defined replace_with)

#do_replace=True
do_refactor=True

refactor_wildcards = ["*.cpp", "*.h"]

refactor_codetype = "cpp"

#refactor_matches = "sRet ?\+= ?("[^"]+");"
#refactor_matches = '(tStrAppend)\(("[^"]+"\));'
#replace_with = "tSTR_APPEND(\2);"

#refactor_matches = '(tStrAppend)'
#replace_with = "tSTR_APPEND(\2);"

#sHTML += "</td>";
# should become -> tSTR_APPEND(sHTML, "</td>");
#tStrAppend(sHTML, "</tr>");
# should become -> tSTR_APPEND(sHTML, "</tr>");
refactor_matches = 'tStrAppend\(([A-Za-z0-9]+), ?("[^"]+")\)'
replace_with = r'tSTR_APPEND(\1, \2)'


##define tSTREAMWRITE(szStr8) m_pStream->Write(szStr8, tCONST_STRLEN(szStr8))
#tStreamAppend(m_pStream, "</span>");
# should become ->
# tSTREAMWRITE(
refactor_matches = 'tStreamAppend\(([A-Za-z_0-9]+), ?("[^"]+")\)'
replace_with = r'tSTREAMWRITE(\1, \2)'
refactor_matches = r'tStreamAppend\(m_pStream, ?("[^"]+")\)'
replace_with = r'tSTREAM_WRITE(m_pStream, \1)'

#refactor_matches = "tStrAppend"
#replace_with = "tSTR_APPEND"

# Don't change the actual function itself
refactor_negmatches =["void tStrAppend\(", "^\s*//", "//tStrAppend\("]

