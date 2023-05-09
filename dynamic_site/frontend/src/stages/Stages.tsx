import Docs from './Docs';
import Plots from './Plots';
import Settings from './Settings';

import InfoBar from '../infobar/InfoBar';

import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';
import { ParameterProp } from './Interfaces';

interface ParameterValue {
  id: string;
  name: string;
  value: string;
  isValid: boolean;
}

function Stages() {
  const [data, setData] = useState({
    docs: [],
    settings: [],
    plots: [],
  });

  const initialParameters: { [id: string]: ParameterValue } = {};
  const [parameters, setParameters] = useState(initialParameters);

  // Compute sends the data and sets the returned data into this stage
  const computeCallback = () => {
    // Collect all the data, if there are any
    const validKeys = Object.keys(parameters).filter(
      (k) => parameters[k].isValid
    );
    const parameterData = {};
    validKeys.forEach(
      (k) => (parameterData[parameters[k].id] = parameters[k].value)
    );

    axios
      .post(`${window.location.href}/compute`, parameterData)
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
        const filterDependency = (d) => {
          // If it doesn't have a dependency simply return it
          if (!d.dependency) {
            return true;
          }
          // Otherwise have a look in all stages if the dependency is activated
          return (
            concat.filter((e) => e.id === d.dependency)[0].activated === true
          );
        };

        // Then filter everything
        const docs = docsUnfiltered.filter(filterDependency);
        const settings = settingsUnfiltered.filter(filterDependency);
        const plots = plotsUnfiltered.filter(filterDependency);

        // Then loop through all parameters and add callback/change function

        const tempParameters: { [id: string]: ParameterValue } = {};
        settings.concat(plots).forEach((stage) => {
          stage.parameters.forEach((parameter: ParameterProp) => {
            tempParameters[parameter.id] = {
              id: parameter.id,
              name: parameter.name,
              value: parameter.default,
              isValid: parameter.default != null,
            };
          });
        });
        setParameters(tempParameters);

        setData({
          docs: docs,
          settings: settings,
          plots: plots,
        });
      });
  };

  const [computeIndex, setComputeIndex] = useState(1);

  useEffect(() => {
    console.log(computeIndex);
    setComputeIndex(computeIndex + 1);
    computeCallback();
  }, []);

  const [updateInfoBar, setUpdateInfoBar] = useState(0);

  function updateParameter(parameter: ParameterValue) {
    // If the new parameter changed its validity, then update the info bar
    if (parameter.isValid !== parameters[parameter.id].isValid) {
      setUpdateInfoBar(updateInfoBar + 1);
    }
    setParameters({ ...parameters, [parameter.id]: parameter });
  }

  return (
    <>
      <InfoBar parameters={parameters} updateFlag={updateInfoBar} />

      <div className='uk-width-1-1 uk-child-width-1-3@m' data-uk-grid>
        <Docs docs={data.docs} />
        <Settings
          settings={data.settings}
          updateParameter={updateParameter}
          computeCallback={computeCallback}
          computeIndex={computeIndex}
        />
        <Plots
          plots={data.plots}
          updateParameter={updateParameter}
          computeIndex={computeIndex}
        />
      </div>
    </>
  );
}
export default Stages;
