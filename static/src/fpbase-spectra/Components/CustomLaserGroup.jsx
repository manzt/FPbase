import React, { useEffect, useRef, useState } from "react"
import Box from "@material-ui/core/Box"
import CustomLaserCreator from "./CustomLaserCreator"
import IconButton from "@material-ui/core/IconButton"
import Button from "@material-ui/core/Button"
import AddIcon from "@material-ui/icons/Add"
import DeleteIcon from "@material-ui/icons/Delete"
import { categoryIcon } from "./FaIcon"
import { useMutation, useQuery } from "react-apollo-hooks"
import {
  UPDATE_ACTIVE_SPECTRA,
  GET_EX_NORM,
  SET_EX_NORM
} from "../client/queries"

const CustomLaserGroup = ({ activeSpectra }) => {
  const laserCounter = useRef(0)
  const [customLasers, setLasers] = useState([])
  const updateSpectra = useMutation(UPDATE_ACTIVE_SPECTRA)
  const {
    data: {
      exNorm: [_, normID]
    }
  } = useQuery(GET_EX_NORM)
  const mutateExNormWave = useMutation(SET_EX_NORM)

  const setExNorm = React.useCallback(
    data => mutateExNormWave({ variables: { data } }),
    [mutateExNormWave]
  )

  const clearNorm = React.useCallback(
    () => mutateExNormWave({ variables: { data: [null, null] } }),
    [mutateExNormWave]
  )

  // const {
  //   data: { activeSpectra }
  // } = useQuery(GET_ACTIVE_SPECTRA)
  useEffect(() => {
    if (activeSpectra && activeSpectra.length > 0) {
      const newLasers = activeSpectra.filter(
        as =>
          as.startsWith("$cl") &&
          !customLasers.find(item => item.startsWith(as.split("_")[0]))
      )

      if (newLasers.length) {
        const inds = newLasers.map(id => +id.split("_")[0].replace("$cl", ""))
        laserCounter.current = Math.max(...inds) + 1
        setLasers([...customLasers, ...newLasers])
      }
    }
  }, [activeSpectra]) // eslint-disable-line

  const addRow = () => {
    setLasers([...customLasers, `$cl${laserCounter.current++}`])
  }

  const removeRow = laser => {
    const laserID = laser.split("_")[0]
    if (laserID === normID) {
      clearNorm()
    }
    setLasers(customLasers.filter(id => !id.startsWith(laserID)))
    updateSpectra({
      variables: {
        remove: [laserID]
      }
    })
  }

  return (
    <div>
      {customLasers.map(laser => (
        <div style={{ width: "100%", margin: "4px 0" }} key={laser}>
          <Box display="flex" alignItems="center">
            {categoryIcon("CL", "rgba(0,0,50,0.4)", {
              style: {
                position: "relative",
                top: 0,
                left: 2,
                height: "1.3rem",
                marginRight: 10
              }
            })}
            <Box flexGrow={1}>
              <CustomLaserCreator
                key={laser.split("_")[0]}
                id={laser}
                setExNorm={setExNorm}
                clearNorm={clearNorm}
                normID={normID}
              />
            </Box>
            <Box>
              <IconButton
                aria-label="Delete"
                color="secondary"
                tabIndex={-1}
                onClick={() => removeRow(laser)}
                style={{
                  padding: "6px 6px",
                  marginRight: 2,
                  marginLeft: 2
                }}
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
        style={{ marginTop: 8, marginLeft: 34 }}
      >
        <AddIcon />
        {`Add Laser`}
      </Button>
    </div>
  )
}

export default CustomLaserGroup
