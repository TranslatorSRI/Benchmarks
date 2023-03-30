import React, {useState, useContext} from "react";
import StoreContext from '../../Utilities/StoreContext';
import styles from './Checkbox.module.scss';

const Checkbox = ({value, children, className}) => {
  const store = useContext(StoreContext);

  const [isChecked, setIsChecked] = useState(false);

  let isCheckedClass = (isChecked) ? styles.checked : styles.unchecked;

  const handleChange = (e) => {
    setIsChecked(e.target.checked);
    if (e.target.checked) {
      store.fetchBenchmark(value);
    } else {
      store.removeBenchmark(value);
    }
  }
  
  return (

    <label className={`${styles.checkbox} ${isCheckedClass} ${className}`}>
      <span className={styles.circle}></span>
      <input type="checkbox" checked={isChecked} onChange={handleChange} />
      <span>{children}</span>
    </label>

  );
}


export default Checkbox;