import React, { useEffect } from "react";
import Sidebar from "../Sidebar/Sidebar";
import styles from './Page.module.scss';


const Page = ({title, children}) => {
  
  useEffect(() => {
    document.title = title || "";
  }, [title]);

  return (
    <div className={`body ${styles.body}`}>
      <div className={styles.bodyContainer}>
        <div className={styles.pageContainer}>
          <Sidebar />
          <div className={styles.right}>
            {children}
          </div>
        </div>
      </div>
    </div>
  )
};

export default Page;