import React, { useEffect } from "react";
import Sidebar from "../Sidebar/Sidebar";
import styles from './Page.module.scss';


const Page = ({title, children, sidebarLinks, handleSidebarLinkClick, handleShowBenchmarks}) => {
  
  useEffect(() => {
    document.title = title || "";
  }, [title]);

  return (
    <div className={`body ${styles.body}`}>
      <div className={styles.bodyContainer}>
        <div className={styles.pageContainer}>
          <Sidebar links={sidebarLinks} handleLinkClick={handleSidebarLinkClick} handleShowBenchmarks={handleShowBenchmarks} />
          <div className={styles.right}>
            {children}
          </div>
        </div>
      </div>
    </div>
  )
};

export default Page;