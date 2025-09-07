# Request Response Cycle

# File Move

### `📤 MavenExplorer.executeMoveFile` ▶ `🐍 views.AjaxRefresh`

The following data parameters are passed from Javascript to Python:

Parameter | Value | Example 
--- | --- | --- 
`action` | Action key | `"file-move"` 
`source` | Source directory URL | `image/upload` 
`target` | Target directory URL | `profiles/pics` 
`files` | JSON encoded list of files to move | `"[{\"index\": 2, \"filename\": \"SomeFile.txt\", \"canEdit\": true}]"`


### `🐍 views.AjaxRefresh` ▶ `📥 MavenExplorer.executeMoveFile`

The following data parameters are passed from Python back to Javascript:

Parameter | Value | Example 
--- | --- | --- 
`action` | Action key | `"file-move"` 
`files-moved` | JSON encoding of files successfully moved | `"[\"SomeFile.txt\"]"`
`file-move-count` | Number of files moved | 1
`ajax` | Dict object of HTML data | See `dir-select` action.  
`message` | Success message to be rendered *if* all files moves successful | Varies
`error` | Error message to be rendered *if* at least one file move failed | Varies
`valid` | `AjaxRefresh()` completed without uncaught errors? | True



