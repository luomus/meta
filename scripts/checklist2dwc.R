# R script to convert FinBIF Checklist into a DwC simple text file
# for publishing to checklistbank

library(httr2)
library(readxl)

req <-
  request("https://api.laji.fi") |>
  req_url_path("v0") |>
  req_url_path_append("taxa") |>
  req_url_query(
    pageSize = 1000,
    includeHidden = "true",
    onlyFinnish = "true",
    selectedFields = paste(
      "id",
      "taxonConceptIds",
      sep = ","
    ),
    access_token = Sys.getenv("FINBIF_ACCESS_TOKEN"),
    page = 1
  )

res <-
  req_perform(req) |>
  resp_body_json()

ans <- res$results

for (i in seq_len(res$lastPage)[-1]) {

  req <- req_url_query(req, page = i)

  res <-
    req_perform(req) |>
    resp_body_json()

  ans <- c(ans, res$results)

}

get_data <- function(x, name) {

  if (hasName(x, name)) {

    getElement(x, name)[[1]]

  } else {

    NA_character_

  }

}

tmp <- tempfile()

download.file(
  file.path(
    "https://cdn.laji.fi",
    "files",
    "checklists",
    "2024",
    "Liite1_Appendix1_Lajiluettelo2024_Checklist2024.xlsx"
  ),
  destfile = tmp,
  quiet = TRUE
)

df <- data.frame(
  Identifier = vapply(ans, getElement, "", "id"),
  taxonConceptID = vapply(ans, get_data, "", "taxonConceptIds")
)

checklist <- read_xlsx(tmp, col_types = "text", progress = FALSE)

checklist <- merge(checklist, df, all.x = TRUE)

names(checklist) <- c(
  "taxonID", "domain", "kingdom", "phylum", "subphylum", "division",
  "class", "subclass", "order", "suborder", "superfamily", "family",
  "subfamily", "tribe", "subtribe", "genus", "subgenus", "aggregate",
  "taxonRank", "scientificName", "scientificNameAuthorship", "vernacularName",
  "swedishName", "altVernacularNames", "experts", "informalGroups",
  "taxonConceptID"
)

checklist <- transform(
  checklist,
  taxonID = paste0("http://tun.fi/", taxonID),
  taxonConceptID = ifelse(
    taxonConceptID == "taxonid:",
    NA_character_,
    sub("taxonid:", "http://taxonid.org/", taxonConceptID)
  ),
  genericName = genus,
  scientificName = ifelse(
    is.na(scientificNameAuthorship),
    scientificName,
    paste(scientificName, scientificNameAuthorship)
  ),
  vernacularName = ifelse(
    grepl("\\(alalaji", vernacularName),
    NA_character_,
    vernacularName
  ),
  language = "fi",
  domain = NULL,
  subphylum = NULL,
  division = NULL,
  subclass = NULL,
  suborder = NULL,
  subgenus = NULL,
  aggregate = NULL,
  swedishName = NULL,
  altVernacularNames = NULL,
  experts = NULL,
  informalGroups = NULL
)

# Remove subgenera from scientificNames
checklist <- transform(
  checklist, scientificName = sub("\\(Eremodrina\\) ", "", scientificName)
)

checklist <- transform(
  checklist, scientificName = sub("\\(Cupressobium\\) ", "", scientificName)
)

checklist <- transform(checklist, scientificName = sub("'", "", scientificName))

checklist <- transform(
  checklist,
  specificEpithet = vapply(strsplit(scientificName, " "), \(x) x[[2L]], "")
)

checklist <- transform(
  checklist,
  parentNameUsage = ifelse(
    taxonRank == "species", genus, paste(genus, specificEpithet)
  )
)

checklist <- subset(
  checklist,
  subset =
    taxonRank %in% c("species", "subspecies", "form", "variety") &
    !grepl("f\\.", specificEpithet) &                               # Remove taxa that don't have legit epithets
    !taxonID == "http://tun.fi/MX.5091289"                          # Remove odd Diatom taxon
)

write.table(
  checklist,
  "species.txt",
  quote = FALSE,
  sep = "\t",
  na = "",
  row.names = FALSE
)
