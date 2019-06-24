import React, { useRef } from "react"
import { SPECTRA_LIST } from "./client/queries"

import { reshapeSpectraInfo } from "./util"
import { SpectraViewer } from "./Components/SpectraViewer"
import OwnersContainer from "./Components/OwnersContainer"
import WelcomeModal from "./Components/WelcomeModal"
import { useCachedQuery } from "./useCachedQuery"
import useSelectors from "./Components/useSelectors"
import MyAppBar from "./Components/MyAppBar"

const App = () => {
  const stash = useCachedQuery(SPECTRA_LIST, "_FPbaseSpectraStash", 5 * 60)
  const owners = useRef({})
  const spectraInfo = useRef({})
  if (stash) {
    const data = reshapeSpectraInfo(stash.spectra)
    owners.current = data.owners
    spectraInfo.current = data.spectraInfo
  }

  const { selectors, changeOwner, removeRow, addRow, clearForm } = useSelectors(
    { owners: owners.current, spectraInfo: spectraInfo.current }
  )

  const storageKey = "_hideFPbaseSpectraWelcome"
  const hide = localStorage.getItem(storageKey) === "true"
  const [checked, setChecked] = React.useState(hide)
  const [open, setOpen] = React.useState(!hide)

  const handleChange = e => {
    localStorage.setItem(storageKey, e.target.checked)
    setChecked(e.target.checked)
  }

  return (
    <>
      <SpectraViewer spectraInfo={spectraInfo.current} />
      {spectraInfo.current && owners.current && (
        <OwnersContainer
          owners={owners.current}
          selectors={selectors}
          addRow={addRow}
          changeOwner={changeOwner}
          removeRow={removeRow}
          clearForm={clearForm}
        />
      )}
      <MyAppBar
        spectraOptions={Object.values(owners.current || {})}
        clearForm={clearForm}
        openHelp={() => setOpen(true)}
      />
      <WelcomeModal
        open={open}
        checked={checked}
        close={() => setOpen(false)}
        handleChange={handleChange}
        isNew={
          Math.round(
            (new Date(2019, 6, 1) - Date.now()) / (1000 * 60 * 60 * 24)
          ) < 120
        }
      />
    </>
  )
}

export default App
