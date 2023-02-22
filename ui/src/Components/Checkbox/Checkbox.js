import React, {useState, useEffect} from "react";
import styles from './Checkbox.module.scss';

const Checkbox = ({name, value, checked, children, handleClick = () => {}, className}) => {

  const [isChecked, setIsChecked] = useState(checked);

  let isCheckedClass = (isChecked) ? styles.checked : styles.unchecked;

  const handleChange = () => {
    setIsChecked(!isChecked);
    handleClick(value);
  }
  
  useEffect(() => {
    setIsChecked(checked);
  }, [checked])

  return (

    <label className={`${styles.checkbox} ${isCheckedClass} ${className}`}>
      <span className={styles.circle}></span>
      <input type="checkbox" defaultChecked={isChecked} name={name} value={value} onChange={handleChange} />
      <span>{children}</span>
    </label>

  );
}


export default Checkbox;