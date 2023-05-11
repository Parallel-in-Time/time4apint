import Docs from './Docs';
import Plots from './Plots';
import Settings from './Settings';

import InfoBar from '../infobar/InfoBar';

import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';

interface ParameterValue {
  id: string;
  name: string;
  value: string;
  isValid: boolean;
}

function Stages() {
  // The received data which are only changed, whenever the compute request is sent
  const [docsData, setDocsData] = useState([]);
  const [settingsData, setSettingsData] = useState([]);
  const [plotsData, setPlotsData] = useState([]);

  // The parameter values which are sent back to the server
  const initialParameters: { [id: string]: ParameterValue } = {};
  const [parameters, setParameters] = useState(initialParameters);

  // The invalid parameters that define the errors in the info bar
  const initialInvalidParameters: string[] = [];
  const [invalidParameters, setInvalidParameters] = useState(
    initialInvalidParameters
  );

  // Compute sends the data and sets the returned data into this stage
  const computeCallback = () => {
    // Collect all the valid data from the parameter input fields, if there are any
    const validKeys = Object.keys(parameters).filter(
      (k) => parameters[k].isValid
    );
    const parameterData: { [id: string]: string } = {};
    validKeys.forEach(
      (k) => (parameterData[parameters[k].id] = parameters[k].value)
    );

    axios
      .post(`${window.location.pathname}/compute`, parameterData)
      .then((response) => {
        // Filter data here for dependencies
        const docsUnfiltered = response.data.docs;
        const settingsUnfiltered = response.data.settings;
        const plotsUnfiltered = response.data.plots;

        // Concatenated to search through all stages
        const concat = docsUnfiltered
          .concat(settingsUnfiltered)
          .concat(plotsUnfiltered);

        // A function to filter the dependencies
        const filterDependency = (d: { dependency: string }) => {
          // If it doesn't have a dependency simply return it
          if (!d.dependency) {
            return true;
          }
          // Otherwise have a look in all stages if the dependency is activated
          return (
            concat.filter((e: { id: string }) => e.id === d.dependency)[0]
              .activated === true
          );
        };

        // Then filter everything and set the data
        setDocsData(() => docsUnfiltered.filter(filterDependency));
        setSettingsData(() => settingsUnfiltered.filter(filterDependency));
        setPlotsData(() => plotsUnfiltered.filter(filterDependency));
      });
  };

  // On startup, send one initial compute request
  useEffect(() => computeCallback(), []);

  // The update parameter callback function that is passed down to the input fields
  const updateParameter = useCallback((parameter: ParameterValue) => {
    setParameters((params) => {
      return { ...params, [parameter.id]: parameter };
    });
  }, []);

  // Whenever the parametrs change, look out for the invalid parameters
  useEffect(() => {
    Object.keys(parameters).forEach((k) => {
      const parameter = parameters[k];

      // Check if its not included but invalid
      const exists = invalidParameters.indexOf(parameter.name);
      if (exists === -1 && !parameter.isValid) {
        // Then add it
        setInvalidParameters((p) => [...p, parameter.name]);
      } else if (
        invalidParameters.indexOf(parameter.name) !== -1 &&
        parameter.isValid
      ) {
        // Check if this parameters is already included but is actually valid
        // Then remove it
        setInvalidParameters((p) => p.filter((e) => e !== parameter.name));
      }
    });
  }, [parameters]);

  return (
    <>
      <InfoBar
        invalidParameters={invalidParameters}
        computeCallback={computeCallback}
      />

      <div className='uk-width-1-1'>
        <div className='uk-child-width-1-3@m uk-grid-column-small' data-uk-grid>
          <div>
            <Docs docs={docsData} />
          </div>
          <div>
            <Settings
              settings={settingsData}
              updateParameter={updateParameter}
            />
          </div>
          <div>
            <Plots plots={plotsData} updateParameter={updateParameter} />
          </div>
        </div>
      </div>
    </>
  );
}
export default Stages;
