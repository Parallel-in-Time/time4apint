import Docs from './Docs';
import Plots from './Plots';
import Settings from './Settings';

import axios from 'axios';
import { useEffect, useReducer, useState } from 'react';

interface ParameterValue {
  id: string;
  value: string;
  isValid: boolean;
}

function parameterReduce(
  parameters: Array<ParameterValue>,
  action: { type: string; parameter: ParameterValue }
) {
  switch (action.type) {
    case 'added':
      if (parameters.some((p) => p.id === action.parameter.id)) {
        return parameters;
      }
      // Only add if the id doesn't exist yet
      return [...parameters, action.parameter];
    case 'changed':
      return parameters.map((p) => {
        if (p.id === action.parameter.id) {
          // TODO: Add actual elements to the info bar and check performance
          if (!action.parameter.isValid) {
            console.log('Adding error', action.parameter.id);
          } else {
            console.log('Removing error if exists error', action.parameter.id);
          }
          return action.parameter;
        }
        return p;
      });
    default:
      throw Error('Unknown action: ' + action.type);
  }
}

function Stages() {
  const [data, setData] = useState({
    docs: [],
    settings: [],
    plots: [],
  });

  const [parameters, parameterDispatch] = useReducer(parameterReduce, []);

  function handleAddParameter(parameter: ParameterValue) {
    parameterDispatch({
      type: 'added',
      parameter: {
        id: parameter.id,
        value: parameter.value,
        isValid: parameter.isValid,
      },
    });
  }

  function handleChangeParameter(parameter: ParameterValue) {
    parameterDispatch({
      type: 'changed',
      parameter: parameter,
    });
  }

  // Compute sends the data and sets the returned data into this stage
  const computeCallback = () => {
    axios.post(`${window.location.href}/compute`, {}).then((response) => {
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
      settings.concat(plots).forEach((stage) => {
        stage.parameters.forEach((parameter) => {
          handleAddParameter(parameter);
        });
      });

      setData({
        docs: docs,
        settings: settings,
        plots: plots,
      });
    });
  };

  useEffect(() => computeCallback(), []);

  return (
    <div className='uk-width-1-1 uk-child-width-1-3@m' data-uk-grid>
      <Docs docs={data.docs} />
      <Settings
        settings={data.settings}
        parameterCallback={handleChangeParameter}
        computeCallback={computeCallback}
      />
      <Plots plots={data.plots} parameterCallback={handleChangeParameter} />
    </div>
  );
}
export default Stages;
