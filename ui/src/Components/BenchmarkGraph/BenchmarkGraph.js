import React, {useCallback, useState, useEffect} from 'react';
import {
  LineChart, Line, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
  Legend,
} from 'recharts';
import styles from './BenchmarkGraph.module.scss';


const BenchmarkGraph = ({title, subtitle, data}) => {

  const [formattedData, setFormattedData] = useState(null);

  const getFormattedData = useCallback((data) => {
    let newData = [];
    for(let i = 0; i < data.k; i++) {
      let newItem = {};
      newItem.precision_at_k = data.metrics.precision_at_k[i];
      newItem.mean_average_precision_at_k = data.metrics.mean_average_precision_at_k[i];
      newItem.recall_at_k = data.metrics.recall_at_k[i];
      newItem.top_k_accuracy = data.metrics.top_k_accuracy[i];
      newData.push(newItem);
    }
    return newData;
  }, []);

  useEffect(() => {
    if(data)
      setFormattedData(getFormattedData(data));
  }, [data, getFormattedData]);

  return (
    <div className={styles.graph}>
      {
        title &&
        <h5 className={styles.graphTitle}>{title}</h5>
      }
      {
        subtitle &&
        <p className={styles.graphSubtitle}>{subtitle}</p>
      }
      {
        data && data.benchmark &&
        <div className={styles.benchmarkDetails}>
          {
            data.benchmark.name && 
            <p><span className='bold'>Benchmark Name:</span> {data.benchmark.name}</p>
          }
          {
            data.benchmark.num_queries && 
            <p><span className='bold'>Number of queries:</span> {data.benchmark.num_queries}</p>
          }
          {
            data.benchmark.num_relevant_results && 
            <p><span className='bold'>Number of relevant results:</span> {data.benchmark.num_relevant_results}</p>
          }
        </div>
      }
      {
        data && 
        <div className={styles.graphContainer}>
          <ResponsiveContainer width="100%" height="100%" >
            <LineChart
              width={500}
              height={400}
              data={formattedData}
              margin={{
                top: 20,
                right: 20,
                left: 20,
                bottom: 20,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <YAxis domain={[0, 1]} />
              <Tooltip />  
              <Legend verticalAlign="top" height={50} />
              <Line type="monotone" dataKey="precision_at_k" stroke="#fc0303" />
              <Line type="monotone" dataKey="recall_at_k" stroke="#22c900" />
              <Line type="monotone" dataKey="mean_average_precision_at_k" stroke="#e303fc" />
              <Line type="monotone" dataKey="top_k_accuracy" stroke="#0032fc" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      }
    </div>
  );
}

export default BenchmarkGraph;