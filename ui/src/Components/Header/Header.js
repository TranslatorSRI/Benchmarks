import React from "react";
import {ReactComponent as Logo} from '../../logo.svg';
import styles from './Header.module.scss';

const Header = ({children}) => {
  
  return (
    <header className={styles.header}>
      <div className={styles.topBar}>
        <div className={styles.container}>
          <div className={styles.left}>
            <div className={styles.logo}><Logo/></div>
            <h1 className={styles.siteHead}>Translator Benchmarks</h1>
          </div>
          <div className={styles.right}>
            
          </div>
        </div>
      </div>
        {children}
    </header>
  );
}

export default Header;