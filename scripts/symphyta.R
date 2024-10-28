## An R script to update names in Taxon Editor 

# load package to read excel file
library(readxl)

symphyta <- read_excel(
  "Symphyta_Finnish_names.xlsx",
  col_names = c("id", "x1", "x2", "newName", "oldName"),
  skip = 2
)
symphyta <- subset(symphyta, newName != oldName | is.na(oldName), -x1:-x2)

# load package to use Chrome DevTools Protocol
library(chromote)

# start a browser session
session <- ChromoteSession$new()
# open browser window
session$view()
# open taxon editor (log in manually user the browser)
session$Page$navigate("https://taxoneditor.laji.fi")

old_input <- "input.obsoleteVernacularName___fi"
new_input <- "input.vernacularName___fi"

log <- list()

for (i in seq_len(nrow(symphyta))) {

  log[[i]] <- list()

  # open taxon page
  log[[i]][["page"]] <- session$Page$navigate(
    sprintf("https://taxoneditor.laji.fi/%s", symphyta[[i, "id"]])
  )
  saveRDS(log, file = "log.rds")
  writeLines(sprintf(" ====== Page open for: %s", symphyta[[i, "id"]]))
  Sys.sleep(2)

  # open the editor tools
  ans <- session$Runtime$evaluate(
    "document.querySelector('div.taxonInfo').click()"
  )
  log[[i]][["click"]] <- ans
  saveRDS(log, file = "log.rds")
  stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
  Sys.sleep(2)

  if (!is.na(symphyta[[i, "oldName"]])) {

    # enter the old name as obsolete
    ans <- session$Runtime$evaluate(
      sprintf(
        "document.querySelector('%s').value = '%s'",
        old_input,
        symphyta[[i, "oldName"]]
      )
    )
    writeLines(sprintf("Obsolete name changed: %s", symphyta[[i, "oldName"]]))
    log[[i]][["old_val"]] <- ans
    saveRDS(log, file = "log.rds")
    stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
    Sys.sleep(2)

    # add save button
    ans <- session$Runtime$evaluate(sprintf("$('%s').keyup()", old_input))
    writeLines(sprintf("Save button added for: %s", symphyta[[i, "oldName"]]))
    log[[i]][["old_sub"]] <- ans
    saveRDS(log, file = "log.rds")
    stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
    Sys.sleep(2)

    # save obsolete name
    ans <- session$Runtime$evaluate(
      "document.querySelector('input.saveButton').click()"
    )
    writeLines(sprintf("Obsolete name saved as: %s", symphyta[[i, "oldName"]]))
    log[[i]][["old_save"]] <- ans
    saveRDS(log, file = "log.rds")
    stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
    Sys.sleep(2)

  }

  # enter the new name
  ans <- session$Runtime$evaluate(
    sprintf(
      "document.querySelector('%s').value = '%s'",
      new_input,
      symphyta[[i, "newName"]]
    )
  )
  writeLines(sprintf("Vernacular name changed: %s", symphyta[[i, "newName"]]))
  log[[i]][["new_val"]] <- ans
  saveRDS(log, file = "log.rds")
  stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
  Sys.sleep(2)

  # add save button
  ans <- session$Runtime$evaluate(sprintf("$('%s').keyup()", new_input))
  writeLines(sprintf("Save button added for: %s", symphyta[[i, "newName"]]))
  log[[i]][["new_sub"]] <- ans
  saveRDS(log, file = "log.rds")
  stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
  Sys.sleep(2)

  # save new name
  ans <- session$Runtime$evaluate(
    "document.querySelector('input.saveButton').click()"
  )
  writeLines(sprintf("Vernacular name saved as: %s", symphyta[[i, "newName"]]))
  log[[i]][["new_save"]] <- ans
  saveRDS(log, file = "log.rds")
  stopifnot(!isTRUE(ans[["result"]][["subtype"]] == "error"))
  Sys.sleep(2)
  writeLines(sprintf("Update complete for: %s", symphyta[[i, "id"]]))

}

