import React, { useEffect, useRef, useState } from "react"
import Box from "@material-ui/core/Box"
import CustomFilterCreator from "./CustomFilterCreator"
import IconButton from "@material-ui/core/IconButton"
import Button from "@material-ui/core/Button"
import AddIcon from "@material-ui/icons/Add"
import DeleteIcon from "@material-ui/icons/Delete"
import { categoryIcon } from "./FaIcon"
import { useQuery, useMutation } from "react-apollo-hooks"
import { GET_ACTIVE_SPECTRA, UPDATE_ACTIVE_SPECTRA } from "../client/queries"

const CustomFilterGroup = () => {
  const filterCounter = useRef(0)
  const [customFilters, setFilters] = useState([])
  const updateSpectra = useMutation(UPDATE_ACTIVE_SPECTRA)

  const addRow = () => {
    setFilters([...customFilters, `$cf${filterCounter.current++}`])
  }

  const removeRow = filter => {
    const filterID = filter.split("_")[0]
    setFilters(customFilters.filter(id => !id.startsWith(filterID)))
    updateSpectra({
      variables: {
        remove: [filterID]
      }
    })
  }

  const {
    data: { activeSpectra }
  } = useQuery(GET_ACTIVE_SPECTRA)
  useEffect(() => {
    if (activeSpectra && activeSpectra.length > 0) {
      const newFilters = activeSpectra.filter(
        as =>
          as.startsWith("$cf") &&
          !customFilters.find(item => item.startsWith(as.split("_")[0]))
      )

      if (newFilters.length) {
        const inds = newFilters.map(id => +id.split("_")[0].replace("$cf", ""))
        filterCounter.current = Math.max(...inds) + 1
        setFilters([...customFilters, ...newFilters])
      }
    }
  }, [activeSpectra]) // eslint-disable-line

  return (
    <div style={{ marginTop: 3 }}>
      {customFilters.map(filter => (
        <div style={{ width: "100%" }} key={filter}>
          <Box display="flex" alignItems="center">
            {categoryIcon("CF", "rgba(0,0,50,0.4)", {
              style: {
                position: "relative",
                top: 0,
                left: 2,
                height: "1.3rem",
                marginRight: 10
              }
            })}
            <Box flexGrow={1}>
              <CustomFilterCreator key={filter.split("_")[0]} id={filter} />
            </Box>
            <Box>
              <IconButton
                aria-label="Delete"
                color="secondary"
                tabIndex={-1}
                onClick={() => removeRow(filter)}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>
        </div>
      ))}
      <Button
        variant="contained"
        color="primary"
        onClick={() => addRow()}
        style={{ marginTop: 8 }}
      >
        <AddIcon />
        {`Add Custom Filter`}
      </Button>
    </div>
  )
}

export default CustomFilterGroup
